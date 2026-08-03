import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import { Mail, Lock, User, Eye, EyeOff, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card } from "@/components/ui/card";
import { Logo } from "@/components/opticrop/Logo";
import { AuthAside } from "@/components/opticrop/AuthAside";
import { cn } from "@/lib/utils";
import { useAuth } from "../lib/auth";
import { toast } from "sonner";

import { useEffect } from "react";

export const Route = createFileRoute("/register")({
  component: Register,
});

function strength(pw: string) {
  let score = 0;
  if (pw.length >= 8) score++;
  if (/[A-Z]/.test(pw) && /[a-z]/.test(pw)) score++;
  if (/\d/.test(pw)) score++;
  if (/[^A-Za-z0-9]/.test(pw)) score++;
  return score; // 0-4
}

const labels = ["Too weak", "Weak", "Fair", "Good", "Strong"];

function Register() {
  const navigate = useNavigate();
  const { register, user } = useAuth();
  const [show, setShow] = useState(false);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [pw, setPw] = useState("");
  const [confirmPw, setConfirmPw] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const score = useMemo(() => strength(pw), [pw]);

  useEffect(() => {
    if (user) {
      navigate({ to: "/app/dashboard" });
    }
  }, [user, navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (pw !== confirmPw) {
      toast.error("Passwords do not match.");
      return;
    }
    setIsSubmitting(true);
    const success = await register({
      fullName: name,
      email,
      phone: "",
      role: "Farmer",
      occupation: "Farmer",
      location: "",
      bio: ""
    }, pw);
    setIsSubmitting(false);

    if (success) {
      toast.success("Account created successfully!");
      navigate({ to: "/app/dashboard" });
    } else {
      toast.error("Registration failed. A user with this email may already exist.");
    }
  };

  return (
    <div className="grid min-h-screen lg:grid-cols-2">
      <AuthAside />
      <div className="flex items-center justify-center px-5 py-12">
        <Card className="animate-fade-up glass w-full max-w-md rounded-[20px] border-border/60 p-8 shadow-[var(--shadow-lift)]">
          <div className="mb-6 lg:hidden"><Logo /></div>
          <h1 className="font-display text-2xl font-700">Create your account</h1>
          <p className="mt-1 text-sm text-muted-foreground">Start optimizing your crops in minutes.</p>

          <form
            className="mt-7 space-y-4"
            onSubmit={handleSubmit}
          >
            <div className="space-y-1.5">
              <Label htmlFor="name">Full Name</Label>
              <div className="relative">
                <User className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  id="name"
                  required
                  placeholder="Jane Farmer"
                  className="h-11 rounded-xl pl-10"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                />
              </div>
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="email">Email Address</Label>
              <div className="relative">
                <Mail className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  id="email"
                  type="email"
                  required
                  placeholder="you@farm.com"
                  className="h-11 rounded-xl pl-10"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="password">Password</Label>
              <div className="relative">
                <Lock className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input id="password" type={show ? "text" : "password"} required value={pw} onChange={(e) => setPw(e.target.value)} placeholder="••••••••" className="h-11 rounded-xl px-10" />
                <button type="button" onClick={() => setShow((s) => !s)} className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground">
                  {show ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
              {pw && (
                <div className="pt-1">
                  <div className="flex gap-1">
                    {[0, 1, 2, 3].map((i) => (
                      <span key={i} className={cn(
                        "h-1.5 flex-1 rounded-full transition-colors",
                        i < score ? (score <= 1 ? "bg-destructive" : score === 2 ? "bg-warning" : score === 3 ? "bg-secondary" : "bg-primary") : "bg-muted",
                      )} />
                    ))}
                  </div>
                  <p className="mt-1 text-xs text-muted-foreground">Strength: {labels[score]}</p>
                </div>
              )}
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="confirm">Confirm Password</Label>
              <div className="relative">
                <Lock className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  id="confirm"
                  type={show ? "text" : "password"}
                  required
                  placeholder="••••••••"
                  className="h-11 rounded-xl pl-10"
                  value={confirmPw}
                  onChange={(e) => setConfirmPw(e.target.value)}
                />
              </div>
            </div>
            <Button type="submit" variant="hero" size="lg" className="w-full" disabled={isSubmitting}>
              {isSubmitting ? "Creating Account..." : "Create Account"} <ArrowRight className="h-4 w-4" />
            </Button>
          </form>

          <p className="mt-6 text-center text-sm text-muted-foreground">
            Already have an account? <Link to="/login" className="font-medium text-primary hover:underline">Login</Link>
          </p>
        </Card>
      </div>
    </div>
  );
}
