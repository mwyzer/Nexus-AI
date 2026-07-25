export default function HomePage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="max-w-3xl text-center">
        <h1 className="text-4xl font-bold tracking-tight sm:text-6xl">
          Nexus AI
        </h1>
        <p className="mt-6 text-xl text-muted-foreground">
          Enterprise AI Knowledge & Agent Platform
        </p>
        <div className="mt-10 flex items-center justify-center gap-4">
          <a
            href="/login"
            className="rounded-md bg-primary px-6 py-3 text-sm font-semibold text-primary-foreground hover:bg-primary/90"
          >
            Sign In
          </a>
          <a
            href="/register"
            className="rounded-md border px-6 py-3 text-sm font-semibold hover:bg-accent"
          >
            Get Started
          </a>
        </div>
      </div>
    </main>
  );
}
