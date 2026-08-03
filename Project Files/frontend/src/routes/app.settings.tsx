import { createFileRoute } from "@tanstack/react-router";
import { Sun, Moon, Upload, RefreshCw, User as UserIcon } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { PageHeader } from "@/components/opticrop/PageHeader";
import { Textarea } from "@/components/ui/textarea";
import { useTheme } from "@/lib/theme";
import { toast } from "sonner";
import { useAuth } from "../lib/auth";
import { useEffect, useState, useRef } from "react";

export const Route = createFileRoute("/app/settings")({
  component: Settings,
});

function Settings() {
  const { theme, toggle } = useTheme();
  const { user, updateProfile } = useAuth();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [avatar, setAvatar] = useState("");
  const [bio, setBio] = useState("");
  const [location, setLocation] = useState("");
  const [occupation, setOccupation] = useState("");

  // Sync component state with global auth state
  useEffect(() => {
    if (user) {
      setFullName(user.fullName || "");
      setEmail(user.email || "");
      setPhone(user.phone || "");
      setAvatar(user.avatar || "");
      setBio(user.bio || "");
      setLocation(user.location || "");
      setOccupation(user.occupation || user.role || "");
    }
  }, [user]);

  const initials = fullName
    .split(" ")
    .filter(Boolean)
    .map((n) => n[0])
    .join("")
    .slice(0, 2)
    .toUpperCase() || "U";

  const handleAvatarFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.size > 2 * 1024 * 1024) {
        toast.error("Avatar image size must be less than 2MB.");
        return;
      }
      const reader = new FileReader();
      reader.onloadend = () => {
        setAvatar(reader.result as string);
        toast.info("Avatar loaded. Press Save Changes to apply.");
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSaveChanges = () => {
    updateProfile({
      fullName,
      email,
      phone,
      avatar,
      bio,
      location,
      occupation,
      role: user?.role || "Farmer", // retain original role
    });
    toast.success("Profile saved successfully!");
  };

  return (
    <div>
      <PageHeader title="Settings" description="Manage your profile, appearance, and model configuration." />

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Profile */}
        <Card className="animate-fade-up rounded-[20px] border-border/70 p-6 shadow-[var(--shadow-soft)]">
          <h2 className="font-display text-lg font-600">Profile</h2>
          
          <div className="mt-5 flex items-center gap-4">
            <Avatar className="h-16 w-16">
              {avatar ? (
                <img src={avatar} alt={fullName} className="h-full w-full object-cover rounded-full" />
              ) : (
                <AvatarFallback className="bg-primary/15 text-lg text-primary">{initials}</AvatarFallback>
              )}
            </Avatar>
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleAvatarFileChange}
              accept="image/*"
              className="hidden"
            />
            <Button
              variant="outline"
              size="sm"
              onClick={() => fileInputRef.current?.click()}
            >
              <UserIcon className="h-4 w-4" /> Change Avatar
            </Button>
          </div>

          <div className="mt-5 grid gap-4 sm:grid-cols-2">
            <div className="space-y-1.5">
              <Label>Full Name</Label>
              <Input
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="h-11 rounded-xl"
              />
            </div>
            <div className="space-y-1.5">
              <Label>Email</Label>
              <Input
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="h-11 rounded-xl"
                type="email"
              />
            </div>
            <div className="space-y-1.5">
              <Label>Phone Number</Label>
              <Input
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="+1 (555) 123-4567"
                className="h-11 rounded-xl"
              />
            </div>
            <div className="space-y-1.5">
              <Label>Location</Label>
              <Input
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                placeholder="California, USA"
                className="h-11 rounded-xl"
              />
            </div>
            <div className="space-y-1.5 sm:col-span-2">
              <Label>Farm / Organization / Occupation</Label>
              <Input
                value={occupation}
                onChange={(e) => setOccupation(e.target.value)}
                className="h-11 rounded-xl"
              />
            </div>
            <div className="space-y-1.5 sm:col-span-2">
              <Label>Bio (Optional)</Label>
              <Textarea
                value={bio}
                onChange={(e) => setBio(e.target.value)}
                placeholder="Tell us about yourself..."
                className="min-h-24 rounded-xl resize-none"
              />
            </div>
          </div>
          
          <Button variant="hero" className="mt-5" onClick={handleSaveChanges}>
            Save Changes
          </Button>
        </Card>

        {/* Appearance */}
        <Card className="animate-fade-up rounded-[20px] border-border/70 p-6 shadow-[var(--shadow-soft)]">
          <h2 className="font-display text-lg font-600">Appearance</h2>
          <div className="mt-5 flex items-center justify-between rounded-xl border border-border/60 bg-muted/40 p-4">
            <div className="flex items-center gap-3">
              <span className="grid h-10 w-10 place-items-center rounded-xl bg-primary/10 text-primary">
                {theme === "dark" ? <Moon className="h-5 w-5" /> : <Sun className="h-5 w-5" />}
              </span>
              <div>
                <p className="text-sm font-600">Dark Mode</p>
                <p className="text-xs text-muted-foreground">Switch between light and dark themes.</p>
              </div>
            </div>
            <Switch checked={theme === "dark"} onCheckedChange={toggle} />
          </div>
        </Card>

        {/* Model management */}
        <Card className="animate-fade-up rounded-[20px] border-border/70 p-6 shadow-[var(--shadow-soft)]">
          <h2 className="font-display text-lg font-600">Model Management</h2>
          <p className="mt-1 text-sm text-muted-foreground">Retrain the model with the latest dataset.</p>
          <div className="mt-5 rounded-xl border border-border/60 bg-muted/40 p-4">
            <p className="text-sm font-600">Random Forest · v2.3.1</p>
            <p className="text-xs text-muted-foreground">Last trained May 10, 2024 · Accuracy 98.6%</p>
            <Button variant="outline" className="mt-4" onClick={() => toast.info("Retraining scheduled (demo)")}>
              <RefreshCw className="h-4 w-4" /> Retrain Model
            </Button>
          </div>
        </Card>

        {/* Dataset upload */}
        <Card className="animate-fade-up rounded-[20px] border-border/70 p-6 shadow-[var(--shadow-soft)]">
          <h2 className="font-display text-lg font-600">Dataset Upload</h2>
          <p className="mt-1 text-sm text-muted-foreground">Upload a new CSV dataset for training.</p>
          <label className="mt-5 flex cursor-pointer flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed border-border/70 bg-muted/30 p-8 text-center transition-colors hover:border-primary/50">
            <span className="grid h-12 w-12 place-items-center rounded-xl bg-primary/10 text-primary"><Upload className="h-6 w-6" /></span>
            <span className="text-sm font-600">Drop your CSV here or click to browse</span>
            <span className="text-xs text-muted-foreground">Max 25MB · .csv only</span>
            <input type="file" accept=".csv" className="hidden" onChange={() => toast.success("Dataset queued (demo)")} />
          </label>
        </Card>
      </div>
    </div>
  );
}
