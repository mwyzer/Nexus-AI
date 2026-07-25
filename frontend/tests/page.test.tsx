import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import HomePage from '../src/app/page';

describe('HomePage', () => {
  it('renders the Nexus AI heading', () => {
    render(<HomePage />);
    expect(screen.getByText('Nexus AI')).toBeDefined();
  });

  it('renders sign in and get started links', () => {
    render(<HomePage />);
    expect(screen.getByText('Sign In')).toBeDefined();
    expect(screen.getByText('Get Started')).toBeDefined();
  });
});
