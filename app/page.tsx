import Link from "next/link";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { ArrowRight, Sparkles, Zap, Shield, Users } from "lucide-react";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-br from-green-800 to-green-700 rounded-lg flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-green-800 to-green-700 bg-clip-text text-transparent">
              SlideGen
            </span>
          </div>
          <div className="flex items-center space-x-4">
            <Link href="/sign-in">
              <Button variant="ghost">Đăng nhập</Button>
            </Link>
            <Link href="/sign-up">
              <Button>Bắt đầu</Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 text-center">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-5xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-green-800 via-green-700 to-green-600 bg-clip-text text-transparent">
            Tạo Slide Tuyệt Đẹp với AI
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Biến ý tưởng của bạn thành bài thuyết trình chuyên nghiệp trong vài
            giây. Tải lên nội dung, chọn template và để AI tạo slide đẹp mắt cho
            bạn.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/sign-up">
              <Button
                size="lg"
                className="bg-gradient-to-r from-green-800 to-green-700 hover:from-green-900 hover:to-green-800"
              >
                Bắt đầu tạo <ArrowRight className="ml-2 w-4 h-4" />
              </Button>
            </Link>
            <Button
              size="lg"
              variant="outline"
              className="border-green-800 text-green-800 hover:bg-green-50"
            >
              Xem Demo
            </Button>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="container mx-auto px-4 py-20">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold mb-4">Tại sao chọn SlideGen?</h2>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Các tính năng AI mạnh mẽ giúp việc tạo bài thuyết trình trở nên dễ
            dàng và chuyên nghiệp.
          </p>
        </div>
        <div className="grid md:grid-cols-3 gap-8">
          <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow">
            <CardHeader>
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <Zap className="w-6 h-6 text-blue-600" />
              </div>
              <CardTitle>Tạo slide bằng AI</CardTitle>
              <CardDescription>
                AI tiên tiến tạo slide chuyên nghiệp từ nội dung của bạn trong
                vài giây
              </CardDescription>
            </CardHeader>
          </Card>
          <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow">
            <CardHeader>
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                <Shield className="w-6 h-6 text-purple-600" />
              </div>
              <CardTitle>Template chuyên nghiệp</CardTitle>
              <CardDescription>
                Chọn từ hàng trăm template được thiết kế chuyên nghiệp
              </CardDescription>
            </CardHeader>
          </Card>
          <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow">
            <CardHeader>
              <div className="w-12 h-12 bg-pink-100 rounded-lg flex items-center justify-center mb-4">
                <Users className="w-6 h-6 text-pink-600" />
              </div>
              <CardTitle>Cộng tác dễ dàng</CardTitle>
              <CardDescription>
                Chia sẻ và cộng tác trên bài thuyết trình với nhóm của bạn
              </CardDescription>
            </CardHeader>
          </Card>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-gradient-to-r from-green-100 via-green-50 to-green-200 py-20">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold text-green-900 mb-4">
            Sẵn sàng biến đổi bài thuyết trình của bạn?
          </h2>
          <p className="text-green-800 mb-8 max-w-2xl mx-auto">
            Tham gia cùng hàng nghìn chuyên gia tạo bài thuyết trình tuyệt đẹp
            với SlideGen AI.
          </p>
          <Link href="/sign-up">
            <Button
              size="lg"
              variant="secondary"
              className="bg-gradient-to-r from-green-800 to-green-700 text-white"
            >
              Bắt đầu miễn phí <ArrowRight className="ml-2 w-4 h-4" />
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-center space-x-2 mb-8">
            <div className="w-8 h-8 bg-gradient-to-br from-green-800 to-green-700 rounded-lg flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-green-800 to-green-700 bg-clip-text text-transparent">
              SlideGen
            </span>
          </div>
          <div className="text-center text-gray-400">
            <p>&copy; 2024 SlideGen. Tất cả quyền được bảo lưu.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
