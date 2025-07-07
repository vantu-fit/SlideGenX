# Authentication Hooks

This directory contains custom React hooks for handling authentication and API calls in the SlideGenX application.

## Hooks Overview

### `useAuth`

Main authentication hook that manages user login, logout, and authentication state.

```typescript
import { useAuth } from "@/hooks/use-auth";

const { user, isLoading, error, login, logout, isAuthenticated } = useAuth();
```

**Returns:**

- `user`: Current user object or null
- `isLoading`: Loading state for authentication operations
- `error`: Error message if authentication fails
- `login(credentials)`: Function to log in user
- `logout()`: Function to log out user
- `isAuthenticated`: Boolean indicating if user is authenticated

### `useAuthToken`

Hook to get the current authentication token.

```typescript
import { useAuthToken } from "@/hooks/use-auth";

const token = useAuthToken();
```

### `useAuthenticatedFetch`

Hook that provides a fetch function with automatic authentication headers.

```typescript
import { useAuthenticatedFetch } from "@/hooks/use-auth";

const authenticatedFetch = useAuthenticatedFetch();

// Usage
const response = await authenticatedFetch("/api/protected-endpoint", {
  method: "POST",
  body: JSON.stringify(data),
});
```

### `useApi`

Generic hook for making authenticated API calls.

```typescript
import { useApi } from "@/hooks/use-api";

const { data, isLoading, error, execute, reset } = useApi("/api/endpoint");

// Execute the API call
await execute({
  method: "POST",
  body: JSON.stringify(data),
});
```

### Specific API Hooks

Pre-configured hooks for common slide operations:

- `useCreateSlide()`: Create a new slide
- `useGetSlides()`: Fetch all slides
- `useUpdateSlide()`: Update an existing slide
- `useDeleteSlide()`: Delete a slide

## Context Provider

### `AuthProvider`

Wrap your app with the AuthProvider to enable authentication context throughout the application.

```typescript
import { AuthProvider } from "@/contexts/auth-context";

function App() {
  return <AuthProvider>{/* Your app components */}</AuthProvider>;
}
```

### `useAuthContext`

Access authentication context in any component.

```typescript
import { useAuthContext } from "@/contexts/auth-context";

function MyComponent() {
  const { user, login, logout } = useAuthContext();

  // Use authentication functions
}
```

## Protected Routes

### `ProtectedRoute`

Component to protect routes that require authentication.

```typescript
import { ProtectedRoute } from "@/components/protected-route";

function DashboardPage() {
  return (
    <ProtectedRoute>
      <Dashboard />
    </ProtectedRoute>
  );
}
```

## Usage Examples

### Login Form

```typescript
import { useAuth } from "@/hooks/use-auth";

function LoginForm() {
  const { login, isLoading, error } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await login({
        username: "user@example.com",
        password: "password",
      });
    } catch (err) {
      console.error("Login failed:", err);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* form fields */}
      <button type="submit" disabled={isLoading}>
        {isLoading ? "Logging in..." : "Login"}
      </button>
      {error && <p className="error">{error}</p>}
    </form>
  );
}
```

### Making API Calls

```typescript
import { useCreateSlide } from "@/hooks/use-api";

function CreateSlideForm() {
  const { execute, isLoading, error } = useCreateSlide();

  const handleCreate = async (slideData) => {
    await execute({
      method: "POST",
      body: JSON.stringify(slideData),
    });
  };

  return (
    <button onClick={() => handleCreate(data)} disabled={isLoading}>
      {isLoading ? "Creating..." : "Create Slide"}
    </button>
  );
}
```

## Environment Variables

Make sure to set the following environment variable:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Error Handling

All hooks include built-in error handling. Errors are stored in the `error` state and can be displayed to users. The hooks also throw errors so you can handle them in try-catch blocks if needed.

## Local Storage

The authentication system uses localStorage to persist:

- `access_token`: JWT token for API authentication
- `user`: User data object

These are automatically managed by the hooks and don't need manual handling.
