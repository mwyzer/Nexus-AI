import {
  Injectable,
  UnauthorizedException,
  ConflictException,
  Inject,
} from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import * as bcrypt from 'bcryptjs';
import * as jwt from 'jsonwebtoken';
import { v4 as uuidv4 } from 'uuid';
import { User } from '../users/user.entity';
import { RegisterDto, LoginDto, AuthResponse } from './auth.dto';

@Injectable()
export class AuthService {
  constructor(
    @InjectRepository(User)
    private readonly userRepo: Repository<User>,
    @Inject('APP_CONFIG')
    private readonly config: {
      jwtAccessSecret: string;
      jwtRefreshSecret: string;
      jwtAccessExpiresIn: string;
      jwtRefreshExpiresIn: string;
    },
  ) {}

  async register(dto: RegisterDto): Promise<AuthResponse> {
    const existing = await this.userRepo.findOne({ where: { email: dto.email } });
    if (existing) {
      throw new ConflictException('Email already registered');
    }

    const passwordHash = await bcrypt.hash(dto.password, 12);
    const user = this.userRepo.create({
      email: dto.email,
      passwordHash,
      displayName: dto.displayName,
      roles: ['user'],
    });

    await this.userRepo.save(user);
    return this.generateTokens(user);
  }

  async login(dto: LoginDto): Promise<AuthResponse> {
    const user = await this.userRepo.findOne({ where: { email: dto.email } });
    if (!user) {
      throw new UnauthorizedException('Invalid email or password');
    }

    if (!user.isActive) {
      throw new UnauthorizedException('Account is deactivated');
    }

    const isPasswordValid = await bcrypt.compare(dto.password, user.passwordHash);
    if (!isPasswordValid) {
      throw new UnauthorizedException('Invalid email or password');
    }

    return this.generateTokens(user);
  }

  async refreshToken(refreshToken: string): Promise<{ accessToken: string; refreshToken: string; expiresIn: number }> {
    try {
      const payload = jwt.verify(refreshToken, this.config.jwtRefreshSecret) as jwt.JwtPayload;
      const user = await this.userRepo.findOne({ where: { id: payload.sub } });

      if (!user || !user.refreshTokenHash) {
        throw new UnauthorizedException('Invalid refresh token');
      }

      const isValid = await bcrypt.compare(refreshToken, user.refreshTokenHash);
      if (!isValid) {
        throw new UnauthorizedException('Invalid refresh token');
      }

      return this.generateTokens(user);
    } catch {
      throw new UnauthorizedException('Invalid or expired refresh token');
    }
  }

  async logout(userId: string): Promise<void> {
    await this.userRepo.update(userId, { refreshTokenHash: null });
  }

  async getProfile(userId: string): Promise<Omit<User, 'passwordHash' | 'refreshTokenHash'>> {
    const user = await this.userRepo.findOne({ where: { id: userId } });
    if (!user) {
      throw new UnauthorizedException('User not found');
    }

    const { passwordHash, refreshTokenHash, ...profile } = user;
    return profile as Omit<User, 'passwordHash' | 'refreshTokenHash'>;
  }

  private async generateTokens(user: User): Promise<AuthResponse> {
    const payload = {
      sub: user.id,
      email: user.email,
      roles: user.roles,
    };

    const accessToken = jwt.sign(payload, this.config.jwtAccessSecret, {
      expiresIn: this.config.jwtAccessExpiresIn,
      jwtid: uuidv4(),
    });

    const refreshToken = jwt.sign(
      { sub: user.id, type: 'refresh' },
      this.config.jwtRefreshSecret,
      {
        expiresIn: this.config.jwtRefreshExpiresIn,
        jwtid: uuidv4(),
      },
    );

    // Store hashed refresh token
    const refreshTokenHash = await bcrypt.hash(refreshToken, 12);
    await this.userRepo.update(user.id, { refreshTokenHash });

    return {
      user: {
        id: user.id,
        email: user.email,
        displayName: user.displayName,
        roles: user.roles,
      },
      accessToken,
      refreshToken,
      expiresIn: 900, // 15 minutes in seconds
    };
  }
}
