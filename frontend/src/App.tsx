import { useEffect } from 'react';
import { AlertTriangle, Bot, FileText, LayoutDashboard, Sliders } from 'lucide-react';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { ProtectedRoute } from './components/ProtectedRoute';
import { AppShell } from './components/layout/AppShell';
import { LoginPage } from './pages/LoginPage';
import { PlaceholderPage } from './pages/PlaceholderPage';
import { useAuthStore } from './store/authStore';

export function App() {
  const token = useAuthStore((state) => state.token);
  const refreshProfile = useAuthStore((state) => state.refreshProfile);

  useEffect(() => {
    if (token) {
      void refreshProfile();
    }
  }, [token, refreshProfile]);

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />

        <Route
          path="/"
          element={
            <ProtectedRoute>
              <AppShell />
            </ProtectedRoute>
          }
        >
          <Route index element={<Navigate to="/chat" replace />} />
          <Route
            path="chat"
            element={
              <PlaceholderPage
                title="Trợ lý Kỹ thuật RAG AI (SSE Streaming)"
                milestone="Sẵn sàng cho Milestone 4.2"
                description="Giao diện hội thoại theo thời gian thực kết nối /api/v1/chat/query qua SSE ReadableStream, hiển thị bảng Markdown mã lỗi, thẻ cảnh báo an toàn và modal xem file PDF tại đúng trang trích dẫn."
                icon={Bot}
                highlights={[
                  'Streaming token thời gian thực qua ReadableStream',
                  'Render bảng mã lỗi Markdown & GFM sắc nét',
                  'Thẻ cảnh báo an toàn công nghiệp nổi bật',
                  'Bấm vào nguồn trích dẫn mở PDF đúng trang',
                ]}
              />
            }
          />
          <Route
            path="sops"
            element={
              <PlaceholderPage
                title="Kho Tài liệu SOP & Kỹ thuật SMT"
                milestone="Sẵn sàng cho Milestone 4.3"
                description="Quản lý danh sách quy trình chuẩn, tải lên tài liệu PDF mới kèm gắn dây chuyền/máy, kích hoạt vector hóa ChromaDB và xem trực tiếp PDF nội bộ qua token xác thực."
                icon={FileText}
                highlights={[
                  'Bảng danh mục 15+ tài liệu SMT & trạng thái Ingestion',
                  'Upload PDF có kiểm tra trùng lặp SHA-256',
                  'Kích hoạt Re-ingest vector hóa bất đồng bộ',
                  'Xem PDF trực tiếp có xác thực JWT',
                ]}
              />
            }
          />
          <Route
            path="tickets"
            element={
              <PlaceholderPage
                title="Phiếu Báo Sự cố & Gợi ý SOP Tự động"
                milestone="Sẵn sàng cho Milestone 4.3"
                description="Tạo và cập nhật vòng đời phiếu sự cố dây chuyền SMT (OPEN -> IN_PROGRESS -> RESOLVED -> CLOSED) kèm thẻ AI Auto-Suggest quy trình khắc phục ngay khi nhập mã lỗi."
                icon={AlertTriangle}
                highlights={[
                  'Gợi ý SOP tức thì qua /incident_tickets/suggest-sop',
                  'Kiểm soát chuyển trạng thái State Machine',
                  'Tính toán tự động thời gian khắc phục MTTR',
                  'Phân quyền thao tác theo vai trò vận hành',
                ]}
              />
            }
          />
          <Route
            path="dashboard"
            element={
              <ProtectedRoute allowedRoles={['SHIFT_ENGINEER', 'FACTORY_MANAGER', 'ADMIN']}>
                <PlaceholderPage
                  title="Dashboard KPI Vận hành Nhà xưởng"
                  milestone="Sẵn sàng cho Milestone 4.4"
                  description="Trực quan hóa chỉ số MTTR, phân bố sự cố theo dây chuyền sản xuất và Top SOP được tra cứu nhiều nhất với Recharts."
                  icon={LayoutDashboard}
                  highlights={[
                    '4 KPI Cards kết nối /api/v1/dashboard/kpi',
                    'Biểu đồ xu hướng MTTR theo tuần (Recharts)',
                    'Biểu đồ tròn phân bố sự cố theo dây chuyền',
                    'Biểu đồ ngang Top quy trình SOP tra cứu nhiều nhất',
                  ]}
                />
              </ProtectedRoute>
            }
          />
          <Route
            path="admin"
            element={
              <ProtectedRoute allowedRoles={['ADMIN']}>
                <PlaceholderPage
                  title="Quản trị Hệ thống, RBAC & Audit Logs"
                  milestone="Sẵn sàng cho Milestone 4.4"
                  description="Khu vực dành riêng cho System Admin để quản lý tài khoản nhân sự 4 vai trò, xem nhật ký truy vấn RAG AI và theo dõi tình trạng ChromaDB / LLM Provider."
                  icon={Sliders}
                  highlights={[
                    'CRUD tài khoản nhân sự & phân vai trò RBAC',
                    'Theo dõi System Status (DB, ChromaDB, LLM Provider)',
                    'Tra cứu Chat Audit Logs kèm độ trễ TTFT & trích dẫn',
                    'Quản lý dây chuyền sản xuất và danh mục máy trạm',
                  ]}
                />
              </ProtectedRoute>
            }
          />
        </Route>

        <Route path="*" element={<Navigate to="/chat" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
