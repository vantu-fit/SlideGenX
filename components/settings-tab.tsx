"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { User, Shield, Globe, Trash2, LogOut, CheckCircle } from "lucide-react";
import { useAuthContext } from "@/contexts/auth-context";
import { useUpdateProfile, useChangePassword } from "@/hooks/use-api";

export function SettingsTab() {
  const router = useRouter();
  const { user, logout, fetchUserInfo } = useAuthContext();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [darkMode, setDarkMode] = useState(false);
  const [language, setLanguage] = useState("en");
  const [emailNotifications, setEmailNotifications] = useState(true);
  const [showSuccess, setShowSuccess] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");

  // API hooks
  const {
    execute: updateProfile,
    isLoading: isUpdatingProfile,
    error: profileError,
  } = useUpdateProfile();
  const {
    execute: changePassword,
    isLoading: isChangingPassword,
    error: passwordError,
  } = useChangePassword();

  // Initialize form with user data
  useEffect(() => {
    if (user) {
      setName(user.full_name || "");
      setEmail(user.email || "");
    }
  }, [user]);

  const handleUpdateProfile = async () => {
    // Basic validation
    if (!name.trim()) {
      alert("Họ tên là bắt buộc!");
      return;
    }

    if (!email.trim()) {
      alert("Email là bắt buộc!");
      return;
    }

    if (!/\S+@\S+\.\S+/.test(email)) {
      alert("Vui lòng nhập địa chỉ email hợp lệ!");
      return;
    }

    try {
      await updateProfile({
        method: "POST",
        body: JSON.stringify({
          full_name: name,
          email: email,
        }),
      });

      // Refresh user info from backend
      await fetchUserInfo();

      setSuccessMessage("Cập nhật hồ sơ thành công!");
      setShowSuccess(true);
      setTimeout(() => {
        setShowSuccess(false);
        setSuccessMessage("");
      }, 3000);
    } catch (err) {
      console.error("Failed to update profile:", err);
    }
  };

  const handleChangePassword = async () => {
    if (!currentPassword) {
      alert("Mật khẩu hiện tại là bắt buộc!");
      return;
    }

    if (!newPassword) {
      alert("Mật khẩu mới là bắt buộc!");
      return;
    }

    if (newPassword.length < 6) {
      alert("Mật khẩu mới phải có ít nhất 6 ký tự!");
      return;
    }

    if (newPassword !== confirmPassword) {
      alert("Mật khẩu không khớp!");
      return;
    }

    try {
      await changePassword({
        method: "POST",
        body: JSON.stringify({
          old_password: currentPassword,
          new_password: newPassword,
        }),
      });

      // Clear form
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");

      setSuccessMessage("Đổi mật khẩu thành công!");
      setShowSuccess(true);
      setTimeout(() => {
        setShowSuccess(false);
        setSuccessMessage("");
      }, 3000);
    } catch (err) {
      console.error("Failed to change password:", err);
    }
  };

  const handleDeleteAccount = () => {
    if (
      confirm(
        "Bạn có chắc chắn muốn xóa tài khoản? Hành động này không thể hoàn tác."
      )
    ) {
      // Simulate account deletion
      alert("Đã bắt đầu xóa tài khoản. Bạn sẽ nhận được email xác nhận.");
    }
  };

  const handleLogout = () => {
    if (confirm("Bạn có chắc chắn muốn đăng xuất?")) {
      logout();
      router.push("/sign-in");
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {showSuccess && (
        <Alert className="border-green-200 bg-green-50">
          <CheckCircle className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-800">
            {successMessage}
          </AlertDescription>
        </Alert>
      )}

      {(profileError || passwordError) && (
        <Alert variant="destructive">
          <AlertDescription>{profileError || passwordError}</AlertDescription>
        </Alert>
      )}

      {/* Profile Settings */}
      <Card>
        <CardHeader>
          <div className="flex items-center space-x-4">
            <User className="w-5 h-5" />
            <div>
              <CardTitle>Cài đặt Hồ sơ</CardTitle>
              <CardDescription>
                Cập nhật thông tin cá nhân và chi tiết hồ sơ của bạn
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center space-x-4">
            <Avatar className="w-20 h-20">
              <AvatarImage src="/placeholder.svg?height=80&width=80" />
              <AvatarFallback className="text-lg">
                {user?.username?.charAt(0).toUpperCase() || "U"}
              </AvatarFallback>
            </Avatar>
            <div>
              <Button variant="outline" size="sm">
                Đổi ảnh
              </Button>
              <p className="text-sm text-gray-600 mt-1">
                JPG, PNG hoặc GIF. Kích thước tối đa 2MB.
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="name">Họ và tên</Label>
              <Input
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">Địa chỉ Email</Label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
          </div>

          <Button onClick={handleUpdateProfile} disabled={isUpdatingProfile}>
            {isUpdatingProfile ? "Đang cập nhật..." : "Cập nhật Hồ sơ"}
          </Button>
        </CardContent>
      </Card>

      {/* Security Settings */}
      <Card>
        <CardHeader>
          <div className="flex items-center space-x-4">
            <Shield className="w-5 h-5" />
            <div>
              <CardTitle>Cài đặt Bảo mật</CardTitle>
              <CardDescription>
                Quản lý mật khẩu và tùy chọn bảo mật của bạn
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="current-password">Mật khẩu hiện tại</Label>
            <Input
              id="current-password"
              type="password"
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="new-password">Mật khẩu mới</Label>
              <Input
                id="new-password"
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="confirm-password">Xác nhận mật khẩu mới</Label>
              <Input
                id="confirm-password"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
              />
            </div>
          </div>

          <Button onClick={handleChangePassword} disabled={isChangingPassword}>
            {isChangingPassword ? "Đang thay đổi..." : "Đổi mật khẩu"}
          </Button>
        </CardContent>
      </Card>

      {/* Preferences */}
      <Card>
        <CardHeader>
          <div className="flex items-center space-x-4">
            <Globe className="w-5 h-5" />
            <div>
              <CardTitle>Tùy chọn</CardTitle>
              <CardDescription>
                Tùy chỉnh trải nghiệm ứng dụng và thông báo của bạn
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Chế độ tối</Label>
              <p className="text-sm text-gray-600">
                Chuyển đổi giữa giao diện sáng và tối
              </p>
            </div>
            <Switch checked={darkMode} onCheckedChange={setDarkMode} />
          </div>

          <Separator />

          <div className="space-y-2">
            <Label htmlFor="language">Ngôn ngữ</Label>
            <Select value={language} onValueChange={setLanguage}>
              <SelectTrigger className="w-full md:w-[200px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="vi">Tiếng Việt</SelectItem>
                <SelectItem value="en">English</SelectItem>
                <SelectItem value="es">Español</SelectItem>
                <SelectItem value="fr">Français</SelectItem>
                <SelectItem value="de">Deutsch</SelectItem>
                <SelectItem value="zh">中文</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <Separator />

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Thông báo Email</Label>
              <p className="text-sm text-gray-600">
                Nhận cập nhật về bài thuyết trình của bạn
              </p>
            </div>
            <Switch
              checked={emailNotifications}
              onCheckedChange={setEmailNotifications}
            />
          </div>
        </CardContent>
      </Card>

      {/* Danger Zone */}
      <Card className="border-red-200">
        <CardHeader>
          <div className="flex items-center space-x-4">
            <Trash2 className="w-5 h-5 text-red-600" />
            <div>
              <CardTitle className="text-red-600">Vùng nguy hiểm</CardTitle>
              <CardDescription>
                Các hành động không thể hoàn tác và có tính hủy diệt
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 p-4 border border-red-200 rounded-lg bg-red-50">
            <div>
              <h4 className="font-medium text-red-800">Xóa tài khoản</h4>
              <p className="text-sm text-red-600">
                Xóa vĩnh viễn tài khoản và tất cả dữ liệu liên quan
              </p>
            </div>
            <Button
              variant="destructive"
              onClick={handleDeleteAccount}
              className="sm:w-auto"
            >
              Xóa tài khoản
            </Button>
          </div>

          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 p-4 border border-gray-200 rounded-lg">
            <div>
              <h4 className="font-medium">Đăng xuất</h4>
              <p className="text-sm text-gray-600">
                Đăng xuất khỏi tài khoản trên thiết bị này
              </p>
            </div>
            <Button
              variant="outline"
              onClick={handleLogout}
              className="sm:w-auto"
            >
              <LogOut className="w-4 h-4 mr-2" />
              Đăng xuất
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
