/**
 * SmartSOP AI - Unified Interactive Demo Bridge
 * Tự động kết nối 6 màn hình UI, mô phỏng dữ liệu RAG, điều hướng thông minh và kịch bản demo chấm thi.
 */

(function () {
  'use strict';

  // 1. DATA MASTER & DEMO STATE
  const DEMO_PERSONAS = {
    'ENG-092': {
      id: 'ENG-092',
      name: 'Nguyễn Văn A',
      role: 'Kỹ sư ca (Shift Engineer)',
      shift: 'Ca 1 (06:00 - 14:00)',
      workshop: 'Xưởng: SMT-Floor-02',
      initials: 'A',
      avatarColor: 'bg-slate-700 text-sky-300',
      badgeStatus: 'ESD Validated',
      startScreen: '../ui_2_rag_assistant/code.html'
    },
    'ADM-001': {
      id: 'ADM-001',
      name: 'Trần Quốc Bảo',
      role: 'Quản lý nhà máy (Plant Manager)',
      shift: 'Toàn ca (Admin 24/7)',
      workshop: 'Ban Quản Đốc Sản Xuất',
      initials: 'B',
      avatarColor: 'bg-purple-900 text-purple-300',
      badgeStatus: 'Full Control',
      startScreen: '../ui_5_kpi_dashboard/code.html'
    },
    'OP-412': {
      id: 'OP-412',
      name: 'Lê Thị Mai',
      role: 'Công nhân vận hành (Operator)',
      shift: 'Ca 1 (06:00 - 14:00)',
      workshop: 'Dây chuyền SMT-01',
      initials: 'M',
      avatarColor: 'bg-emerald-900 text-emerald-300',
      badgeStatus: 'Operator Level 2',
      startScreen: '../ui_3_sop_documents/code.html'
    }
  };

  const SOP_DATABASE = {
    'SOP-SMT-001': {
      code: 'SOP-SMT-001',
      title: 'Quy trình xử lý lỗi Feeder & Kẹt linh kiện Fuji NXT',
      device: 'FUJI NXT III',
      line: 'SMT-Line 1',
      rev: 'Rev. 2.3',
      pages: '18 Trang',
      similarity: '0.98 • FAISS',
      pdfName: 'SOP-SMT-001_v2.3_Final.pdf',
      pageNumber: 4,
      totalPage: 18,
      sectionTitle: 'Mục 4.2: Xử lý sự cố kẹt cuộn cấp liệu Feeder (Mã lỗi E-204 / Pickup Reject)',
      chunkHighlight: 'Đoạn văn bản kỹ thuật này đã được chỉ mục hóa vào mô hình Trợ lý Kỹ thuật AI để tự động kích hoạt khi có sự cố Feeder mã E-204.',
      steps: [
        { num: '01', text: 'Nhấn nút dừng khẩn cấp STOP cụm gắp (Module Stop). Không tắt nguồn chính (Main Breaker). Chờ cụm X-Y Beam lùi hoàn toàn về vị trí Home (Park Mode).' },
        { num: '02', text: 'Gạt cần nhả chốt Feeder W08b theo góc 45 độ. Dùng ngón tay cái ấn nhẹ ngàm khóa số 2. Rút toàn bộ cuộn linh kiện 8mm ra khỏi bàn máy gá đặt (Feeder Bank).' },
        { num: '03', text: 'Kiểm tra cảm biến quang học và cuộn màng Cover Tape. Soi đèn LED kiểm tra lens thu phát. Nếu phát hiện màng dính cover tape bị xé rách hoặc kẹt bánh răng sao (Sprocket), tuyệt đối không kéo cưỡng bức.' },
        { num: '04', text: 'Cắt bỏ 3 mắt băng dính thừa và hiệu chuẩn lại cữ gắp. Dùng kéo chống tĩnh điện cắt vuông góc. Nạp lại màng vào rãnh thu hồi màng thải và ấn nút Feed test 01 nhịp trên thân Feeder.' }
      ]
    },
    'SOP-REFLOW-02': {
      code: 'SOP-REFLOW-02',
      title: 'Xử lý sai lệch nhiệt độ lò hàn Reflow Heller 1913 Mk5',
      device: 'Heller 1913 Mk5',
      line: 'SMT-Line 1',
      rev: 'Rev. 1.8',
      pages: '26 Trang',
      similarity: '0.95 • pgvector',
      pdfName: 'SOP-REFLOW-02_v1.8_Approved.pdf',
      pageNumber: 7,
      totalPage: 26,
      sectionTitle: 'Mục 2.4: Hiệu chỉnh sai lệch profile nhiệt độ buồng gia nhiệt số 3 (Mã lỗi T-102)',
      chunkHighlight: 'Dữ liệu cảm biến nhiệt độ thermocouple buồng số 3 báo vượt ngưỡng dung sai IPC Class 3 (+4.2°C). Cần can thiệp cân bằng luồng khí đối lưu Nitrogen.',
      steps: [
        { num: '01', text: 'Giảm tốc độ băng chuyền Mesh Belt từ 85 cm/phút xuống 80 cm/phút để ổn định thời gian ngâm nhiệt Soak Zone.' },
        { num: '02', text: 'Kiểm tra lưu lượng khí N2 (Nitrogen Flow Rate), đảm bảo áp suất buồng duy trì ổn định ở mức 15-20 PPM O2.' },
        { num: '03', text: 'Dùng thiết bị đo nhiệt độ KIC K2 Profiler gắn trên bo mạch mẫu chạy kiểm tra đường cong nhiệt độ thực tế.' },
        { num: '04', text: 'Cân chỉnh thông số PID Heater Zone 3 trên màn hình điều khiển cảm ứng và lưu profile cấu hình chuẩn SAC305.' }
      ]
    },
    'SOP-AOI-003': {
      code: 'SOP-AOI-003',
      title: 'Tiêu chuẩn kiểm tra quang học 3D AOI Koh Young',
      device: 'Koh Young 3D',
      line: 'QA-Line 2',
      rev: 'Rev. 3.1',
      pages: '34 Trang',
      similarity: '0.99 • Hybrid RAG',
      pdfName: 'SOP-AOI-003_Rev3.1_Full.pdf',
      pageNumber: 12,
      totalPage: 34,
      sectionTitle: 'Mục 5.1: Xử lý lỗi mất dấu định vị Fiducial Mark bo mạch PCB (Mã lỗi A-105)',
      chunkHighlight: 'Hệ thống camera đo độ cao quang học 3D không tìm thấy mốc chuẩn tọa độ Fiducial do bụi bám hoặc độ phản quang bề mặt đồng bị oxy hóa.',
      steps: [
        { num: '01', text: 'Dừng băng tải nạp PCB của máy AOI. Dùng kính lúp kiểm tra điểm Fiducial Mark trên góc bo mạch PCB.' },
        { num: '02', text: 'Lau sạch thấu kính camera quang học bằng giấy lau chuyên dụng phòng sạch thấm cồn IPA 99.7%.' },
        { num: '03', text: 'Điều chỉnh cường độ vòng đèn LED chiếu sáng (Ring Light) trên phần mềm Koh Young từ mức 60% lên 75%.' },
        { num: '04', text: 'Chạy tính năng Teach Fiducial Mark thủ công và lưu ngưỡng nhận diện vào job kiểm tra hiện tại.' }
      ]
    },
    'SOP-CLEAN-004': {
      code: 'SOP-CLEAN-004',
      title: 'Quy trình an toàn vệ sinh phòng sạch Class 10,000 ISO',
      device: 'Toàn xưởng',
      line: 'Toàn xưởng',
      rev: 'Rev. 1.0',
      pages: '12 Trang',
      similarity: '0.88 • Vectorized',
      pdfName: 'SOP-CLEAN-004_Cleanroom_SOP.pdf',
      pageNumber: 2,
      totalPage: 12,
      sectionTitle: 'Mục 1.2: Tiêu chuẩn ra vào phòng sạch và chống tĩnh điện ESD',
      chunkHighlight: 'Quy định trang phục phòng sạch, kiểm tra máy đo điện trở vòng đeo tay ESD wrist strap hàng ngày trước khi vào dây chuyền sản xuất.',
      steps: [
        { num: '01', text: 'Mặc đầy đủ quần áo phòng sạch, trùm đầu, khẩu trang và giày bảo hộ chống tĩnh điện tại phòng đệm Air Shower.' },
        { num: '02', text: 'Đứng trong buồng thổi bụi Air Shower tối thiểu 15 giây, xoay người 360 độ theo tín hiệu đèn xanh.' },
        { num: '03', text: 'Đo điện trở tiếp đất của vòng đeo tay tĩnh điện tại máy test cổng ra vào; giá trị chuẩn đạt từ 750kΩ đến 10MΩ.' },
        { num: '04', text: 'Quẹt thẻ RFID nhân viên để mở khóa cửa từ bước vào khu vực dây chuyền SMT.' }
      ]
    }
  };

  const QUERY_TEMPLATES = {
    'E-204': {
      code: 'E-204',
      badge: 'Mã: E-204',
      device: 'Thiết bị: FUJI-NXT-03',
      module: 'Module: Feeder W08b (8mm)',
      question: 'Máy gắp linh kiện báo lỗi E-204 kẹt cuộn feeder W08b tại trạm số 3, xử lý thế nào để không lệch tọa độ bo mạch?',
      diagnosis: 'Băng keo màng bọc linh kiện kích thước 0402 bị đứt kẹt trong bánh răng hoặc lực căng cuộn feeder W08b vượt ngưỡng cảm biến mô-men xoắn (Torque Sensor > 1.2Nm), dẫn đến tín hiệu dừng khẩn E-204 để tránh trượt bước động cơ.',
      targetSop: 'SOP-SMT-001',
      page: 4,
      docTitle: 'SOP-SMT-001 (Rev 2.3)',
      docDesc: 'Quy trình xử lý lỗi Pick & Place và Kẹt Feeder (Trang 4)',
      steps: [
        { num: '01', title: 'Mở nắp bảo vệ số 2', text: 'Kiểm tra đèn LED sensor trạng thái tại slot nạp Slot F-14. Bắt buộc dừng an toàn.', required: true },
        { num: '02', title: 'Gạt cần nhả khóa', text: 'Nhấn Release Lever màu xanh lá để tháo cụm cuộn feeder W08b ra khỏi rãnh nạp module máy gắp.' },
        { num: '03', title: 'Vệ sinh quang học', text: 'Cắt bỏ đúng 3 mắt băng dính linh kiện bị biến dạng, làm sạch bụi sợi quang cảm biến bằng tăm bông nhúng cồn IPA 99%.' },
        { num: '04', title: 'Hiệu chuẩn Zero', text: 'Nạp lại cuộn vào rãnh dẫn hướng, căn thẳng lỗ sprocket hole của băng tải và nhấn nút [Reset Lỗi & Zero-Calibrate] trên panel.' }
      ]
    },
    'T-102': {
      code: 'T-102',
      badge: 'Mã: T-102',
      device: 'Thiết bị: HELLER-1913-MK5',
      module: 'Module: Buồng nhiệt số 3 (Soak Zone)',
      question: 'Lò hàn Reflow buồng số 3 báo lỗi T-102 lệch nhiệt độ buồng +4.2°C so với profile hàn chì SAC305, khắc phục thế nào?',
      diagnosis: 'Cảm biến thermocouple buồng 3 ghi nhận nhiệt độ thực tế 184.2°C (ngưỡng chuẩn 180.0°C ± 2°C). Nguyên nhân do quạt đối lưu tuần hoàn khí Nitrogen buồng 3 bị rung lệch trục hoặc điện trở gia nhiệt heater cần cân chỉnh PID.',
      targetSop: 'SOP-REFLOW-02',
      page: 7,
      docTitle: 'SOP-REFLOW-02 (Rev 1.8)',
      docDesc: 'Quy trình xử lý sai lệch nhiệt độ lò hàn Reflow Heller (Trang 7)',
      steps: [
        { num: '01', title: 'Điều chỉnh băng tải', text: 'Giảm tốc độ xích tải từ 85 cm/phút xuống 80 cm/phút để tránh sốc nhiệt linh kiện BGA.', required: true },
        { num: '02', title: 'Kiểm tra van khí N2', text: 'Đo áp suất van cấp khí Nitrogen buồng 3, đảm bảo duy trì nồng độ O2 dưới 20 PPM.' },
        { num: '03', title: 'Hiệu chuẩn PID nhiệt', text: 'Truy cập màn hình SCADA lò hàn, nhập thông số bù trừ Offset nhiệt độ -4.0°C cho buồng gia nhiệt số 3.' },
        { num: '04', title: 'Chạy bo mạch đo test', text: 'Dùng thiết bị KIC K2 Profiler gắn cảm biến nhiệt độ chạy thử nghiệm kiểm tra đường cong hồi đáp nhiệt.' }
      ]
    },
    'A-105': {
      code: 'A-105',
      badge: 'Mã: A-105',
      device: 'Thiết bị: KOH-YOUNG-3D',
      module: 'Module: Camera 3D SPI/AOI',
      question: 'Máy kiểm tra quang học 3D AOI báo lỗi A-105 không nhận diện được điểm Fiducial Mark trên bo mạch PCB, xử lý thế nào?',
      diagnosis: 'Hệ thống nhận diện quang học camera 3D báo lỗi ngưỡng tương phản thấp (Contrast Threshold < 40%) tại điểm mốc chuẩn bo mạch số 1, dẫn đến không căn chỉnh được hệ trục tọa độ X-Y.',
      targetSop: 'SOP-AOI-003',
      page: 12,
      docTitle: 'SOP-AOI-003 (Rev 3.1)',
      docDesc: 'Tiêu chuẩn kiểm tra quang học 3D AOI Koh Young (Trang 12)',
      steps: [
        { num: '01', title: 'Vệ sinh thấu kính', text: 'Dùng khăn lau chuyên dụng phòng sạch thấm cồn IPA lau sạch bề mặt thấu kính camera quang học.', required: true },
        { num: '02', title: 'Kiểm tra điểm Fiducial', text: 'Dùng kính lúp x10 kiểm tra điểm mạ vàng/thiếc trên PCB có bị oxy hóa hoặc dính bụi kem hàn không.' },
        { num: '03', title: 'Tăng sáng đèn LED', text: 'Tăng cường độ ánh sáng chiếu xuyên góc (Coaxial Light) từ 60% lên 75% trong phần mềm Koh Young.' },
        { num: '04', title: 'Teach mốc chuẩn lại', text: 'Chọn chế độ Manual Teach Fiducial trên màn hình AOI, căn tâm chữ thập vào mốc chuẩn và lưu lại job.' }
      ]
    },
    'R-088': {
      code: 'R-088',
      badge: 'Mã: R-088',
      device: 'Thiết bị: KUKA-KR6',
      module: 'Module: Cụm giác hút chân không',
      question: 'Robot gắp dỡ mạch báo lỗi R-088 áp suất hút chân không giảm xuống -0.12 bar không nhấc được khay bo mạch, cách xử lý?',
      diagnosis: 'Cảm biến áp suất chân không phát hiện rò rỉ khí tại núm giác hút Silicon số 2 hoặc bộ lọc khí Venturi Ejector bị tắc bụi xơ sợi carton, làm giảm lực giữ khay PCB.',
      targetSop: 'SOP-SMT-001',
      page: 15,
      docTitle: 'SOP-SMT-001 (Phụ lục Robot)',
      docDesc: 'Quy trình kiểm tra hệ thống khí nén & giác hút chân không Robot KUKA',
      steps: [
        { num: '01', title: 'Dừng chu trình Robot', text: 'Nhấn nút Tạm Dừng (Hold) trên Teach Pendant điều khiển Robot KUKA.', required: true },
        { num: '02', title: 'Kiểm tra núm giác hút', text: 'Kiểm tra giác hút Silicon màu xanh, nếu bị nứt hoặc cong vênh mép hút cần thay núm mới.' },
        { num: '03', title: 'Vệ sinh lõi lọc khí', text: 'Tháo cốc lọc bụi chân không mini, dùng súng xịt khí nén làm sạch lõi lọc kim loại xốp.' },
        { num: '04', title: 'Test áp suất chân không', text: 'Kích hoạt van đóng mở bằng tay trên màn hình HMI, xác nhận đồng hồ đo đạt ngưỡng chuẩn ≤ -0.65 bar.' }
      ]
    }
  };

  // Helper: Current page detection
  function getCurrentPageName() {
    const path = window.location.pathname;
    if (path.includes('ui_1_login')) return 'ui_1_login';
    if (path.includes('ui_2_rag_assistant')) return 'ui_2_rag_assistant';
    if (path.includes('ui_3_sop_documents')) return 'ui_3_sop_documents';
    if (path.includes('ui_4_incident_tickets')) return 'ui_4_incident_tickets';
    if (path.includes('ui_5_kpi_dashboard')) return 'ui_5_kpi_dashboard';
    if (path.includes('ui_6_system_admin')) return 'ui_6_system_admin';
    return 'hub';
  }

  // Helper: Get user state
  function getActiveUser() {
    const saved = localStorage.getItem('smartsop_current_user');
    if (saved && DEMO_PERSONAS[saved]) {
      return DEMO_PERSONAS[saved];
    }
    return DEMO_PERSONAS['ENG-092'];
  }

  function setActiveUser(userId) {
    if (DEMO_PERSONAS[userId]) {
      localStorage.setItem('smartsop_current_user', userId);
      updateUserUI();
    }
  }

  // Update profile widgets on the current page
  function updateUserUI() {
    const user = getActiveUser();
    // Bottom profile cards
    const nameEl = document.querySelector('[data-purpose="user-shift-profile"] h4, h4.text-slate-100');
    const shiftEl = document.querySelector('[data-purpose="user-shift-profile"] p, p.text-slate-400.font-mono');
    const avatarEl = document.querySelector('[data-purpose="user-shift-profile"] .w-8.h-8, .relative .w-8.h-8');
    const workshopEl = document.querySelector('[data-purpose="user-shift-profile"] span:first-child');

    if (nameEl && !nameEl.closest('[data-purpose="examiner-demo-selector"]')) {
      nameEl.textContent = user.name;
    }
    if (shiftEl && !shiftEl.closest('[data-purpose="examiner-demo-selector"]')) {
      shiftEl.textContent = user.shift;
    }
    if (avatarEl && !avatarEl.closest('[data-purpose="examiner-demo-selector"]')) {
      avatarEl.textContent = user.initials;
    }
  }

  // 2. REWIRE SIDEBAR NAV LINKS ACROSS ALL PAGES
  function rewireNavigationLinks() {
    const currentPage = getCurrentPageName();
    if (currentPage === 'ui_1_login') return;

    const nav = document.querySelector('nav[aria-label="Main Navigation"], aside nav');
    if (!nav) return;

    const links = nav.querySelectorAll('a');
    if (links.length >= 5) {
      links[0].href = '../ui_5_kpi_dashboard/code.html';
      links[1].href = '../ui_2_rag_assistant/code.html';
      links[2].href = '../ui_3_sop_documents/code.html';
      links[3].href = '../ui_4_incident_tickets/code.html';
      links[4].href = '../ui_6_system_admin/code.html';

      // Set tooltips
      links[0].title = 'Dashboard KPI & Vận hành sản xuất (UI 5)';
      links[1].title = 'Trợ Lý AI Tra Cứu Sự Cố & SOP (UI 2)';
      links[2].title = 'Kho Tài Liệu SOP & PDF Viewer (UI 3)';
      links[3].title = 'Quản Lý Phiếu Sự Cố Máy Móc (UI 4)';
      links[4].title = 'Quản Trị Hệ Thống & Cấu Hình Master Data (UI 6)';
    }

    // Rewire logout button
    const logoutBtn = document.querySelector('button[title*="Chuyển ca"], button[title*="log-out"], button[title*="Đăng xuất"]');
    if (logoutBtn) {
      logoutBtn.onclick = function (e) {
        e.preventDefault();
        showToast('Đang đăng xuất ca làm việc...', 'info');
        setTimeout(() => {
          window.location.href = '../ui_1_login/code.html';
        }, 500);
      };
    }

    // Rewire Brand Logo
    const brandLogo = document.querySelector('aside .h-16.flex.items-center');
    if (brandLogo) {
      brandLogo.style.cursor = 'pointer';
      brandLogo.onclick = () => {
        window.location.href = '../ui_5_kpi_dashboard/code.html';
      };
    }
  }

  // 3. TOAST NOTIFICATION UTILITY
  function showToast(message, type = 'success') {
    let container = document.getElementById('smartsop-toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'smartsop-toast-container';
      container.className = 'fixed top-5 right-5 z-[9999] flex flex-col gap-2 pointer-events-none';
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    const colors = {
      success: 'bg-emerald-950 border-emerald-500/60 text-emerald-300 shadow-emerald-950/50',
      info: 'bg-sky-950 border-cyan-500/60 text-cyan-300 shadow-sky-950/50',
      warning: 'bg-amber-950 border-amber-500/60 text-amber-300 shadow-amber-950/50',
      error: 'bg-rose-950 border-rose-500/60 text-rose-300 shadow-rose-950/50'
    };

    toast.className = `pointer-events-auto flex items-center gap-2.5 px-4 py-3 rounded-lg border shadow-xl text-xs font-mono transition-all duration-300 transform translate-x-12 opacity-0 ${colors[type] || colors.info}`;
    toast.innerHTML = `
      <span class="w-2 h-2 rounded-full ${type === 'success' ? 'bg-emerald-400' : type === 'warning' ? 'bg-amber-400' : 'bg-cyan-400'} animate-pulse"></span>
      <span class="font-medium">${message}</span>
    `;

    container.appendChild(toast);
    requestAnimationFrame(() => {
      toast.classList.remove('translate-x-12', 'opacity-0');
    });

    setTimeout(() => {
      toast.classList.add('translate-x-12', 'opacity-0');
      setTimeout(() => toast.remove(), 300);
    }, 3200);
  }

  // 4. FLOATING QUICK SWITCHER & DEMO DRAWER
  function injectFloatingDemoWidget() {
    if (document.getElementById('smartsop-floating-widget')) return;

    const widget = document.createElement('div');
    widget.id = 'smartsop-floating-widget';
    widget.className = 'fixed bottom-4 right-4 z-[9990] flex flex-col items-end font-sans select-none';

    widget.innerHTML = `
      <!-- Collapsible Panel -->
      <div id="smartsop-demo-panel" class="hidden mb-2 w-80 max-h-[85vh] overflow-y-auto bg-[#0b1326]/95 backdrop-blur-xl border border-cyan-500/40 rounded-xl shadow-2xl shadow-black/80 text-slate-200 p-4 transition-all">
        <!-- Panel Header -->
        <div class="flex items-center justify-between pb-3 mb-3 border-b border-slate-800">
          <div class="flex items-center gap-2">
            <span class="p-1 rounded bg-cyan-950 border border-cyan-500/40 text-cyan-400">⚡</span>
            <div>
              <div class="text-xs font-bold text-white tracking-wide">SmartSOP Demo Navigator</div>
              <div class="text-[10px] text-slate-400 font-mono">Bảng Điều Hướng & Kịch Bản Chấm Thi</div>
            </div>
          </div>
          <button id="smartsop-close-panel" class="text-slate-400 hover:text-white p-1 rounded hover:bg-slate-800 text-xs">✕</button>
        </div>

        <!-- 1. Screen Jump Menu -->
        <div class="mb-3">
          <div class="text-[10px] uppercase font-mono tracking-wider text-cyan-400 font-bold mb-1.5 flex items-center justify-between">
            <span>Chọn Màn Hình Trực Tiếp:</span>
            <span class="text-slate-500 font-normal">6 Màn hình</span>
          </div>
          <div class="grid grid-cols-2 gap-1.5 text-[11px]">
            <a href="../ui_1_login/code.html" class="p-2 rounded bg-[#131b2e] hover:bg-sky-950 border border-slate-700/80 hover:border-cyan-500/50 flex flex-col gap-0.5 transition-colors">
              <span class="font-bold text-slate-200">1. Đăng Nhập</span>
              <span class="text-[9px] text-slate-400 font-mono">Auth & RFID</span>
            </a>
            <a href="../ui_2_rag_assistant/code.html" class="p-2 rounded bg-[#131b2e] hover:bg-sky-950 border border-slate-700/80 hover:border-cyan-500/50 flex flex-col gap-0.5 transition-colors">
              <span class="font-bold text-cyan-300">2. Trợ Lý RAG AI</span>
              <span class="text-[9px] text-slate-400 font-mono">Chat hỏi lỗi SOP</span>
            </a>
            <a href="../ui_3_sop_documents/code.html" class="p-2 rounded bg-[#131b2e] hover:bg-sky-950 border border-slate-700/80 hover:border-cyan-500/50 flex flex-col gap-0.5 transition-colors">
              <span class="font-bold text-slate-200">3. Kho SOP & PDF</span>
              <span class="text-[9px] text-slate-400 font-mono">PDF Chunk Viewer</span>
            </a>
            <a href="../ui_4_incident_tickets/code.html" class="p-2 rounded bg-[#131b2e] hover:bg-sky-950 border border-slate-700/80 hover:border-cyan-500/50 flex flex-col gap-0.5 transition-colors">
              <span class="font-bold text-amber-300">4. Phiếu Sự Cố</span>
              <span class="text-[9px] text-slate-400 font-mono">Quản lý Ticket</span>
            </a>
            <a href="../ui_5_kpi_dashboard/code.html" class="p-2 rounded bg-[#131b2e] hover:bg-sky-950 border border-slate-700/80 hover:border-cyan-500/50 flex flex-col gap-0.5 transition-colors">
              <span class="font-bold text-slate-200">5. Dashboard KPI</span>
              <span class="text-[9px] text-slate-400 font-mono">MTTR & SCADA</span>
            </a>
            <a href="../ui_6_system_admin/code.html" class="p-2 rounded bg-[#131b2e] hover:bg-sky-950 border border-slate-700/80 hover:border-cyan-500/50 flex flex-col gap-0.5 transition-colors">
              <span class="font-bold text-slate-200">6. Quản Trị HT</span>
              <span class="text-[9px] text-slate-400 font-mono">Master Data/RBAC</span>
            </a>
          </div>
        </div>

        <!-- 2. Persona Switcher -->
        <div class="mb-3 pt-2.5 border-t border-slate-800">
          <div class="text-[10px] uppercase font-mono tracking-wider text-slate-400 font-bold mb-1.5 flex items-center justify-between">
            <span>Đổi Vai Trò Demo (Persona):</span>
            <span class="text-emerald-400 text-[10px]" id="current-persona-badge">ENG-092</span>
          </div>
          <div class="space-y-1">
            <button data-user="ENG-092" class="demo-user-btn w-full text-left p-1.5 rounded bg-[#131b2e] hover:bg-sky-950/60 border border-slate-700/60 text-xs flex items-center justify-between">
              <div>
                <span class="font-semibold text-sky-300">👨‍🔧 Kỹ sư ca</span>
                <span class="text-[10px] text-slate-400 ml-1">Nguyễn Văn A (ENG-092)</span>
              </div>
              <span class="text-[9px] font-mono text-emerald-400">Shift 1</span>
            </button>
            <button data-user="ADM-001" class="demo-user-btn w-full text-left p-1.5 rounded bg-[#131b2e] hover:bg-sky-950/60 border border-slate-700/60 text-xs flex items-center justify-between">
              <div>
                <span class="font-semibold text-purple-300">👔 Quản lý nhà máy</span>
                <span class="text-[10px] text-slate-400 ml-1">Trần Quốc Bảo (ADM-001)</span>
              </div>
              <span class="text-[9px] font-mono text-purple-400">Admin</span>
            </button>
            <button data-user="OP-412" class="demo-user-btn w-full text-left p-1.5 rounded bg-[#131b2e] hover:bg-sky-950/60 border border-slate-700/60 text-xs flex items-center justify-between">
              <div>
                <span class="font-semibold text-emerald-300">👷 Công nhân</span>
                <span class="text-[10px] text-slate-400 ml-1">Lê Thị Mai (OP-412)</span>
              </div>
              <span class="text-[9px] font-mono text-emerald-400">Operator</span>
            </button>
          </div>
        </div>

        <!-- 3. Guided Scenarios -->
        <div class="pt-2.5 border-t border-slate-800">
          <div class="text-[10px] uppercase font-mono tracking-wider text-amber-400 font-bold mb-1.5">
            🎯 Kịch Bản Trình Diễn Báo Cáo:
          </div>
          <div class="space-y-1.5">
            <button id="scenario-1-btn" class="w-full text-left p-2 rounded bg-amber-950/40 hover:bg-amber-900/50 border border-amber-600/40 text-xs text-amber-200 flex flex-col gap-0.5">
              <span class="font-bold flex items-center gap-1">
                <span>⚡ Luồng 1: Xử lý sự cố máy SMT E-204</span>
              </span>
              <span class="text-[10px] text-slate-400 font-mono">Chat RAG ➔ Xem SOP PDF ➔ Đóng Ticket ➔ Xem KPI</span>
            </button>
            <button id="scenario-2-btn" class="w-full text-left p-2 rounded bg-sky-950/40 hover:bg-sky-900/50 border border-sky-600/40 text-xs text-sky-200 flex flex-col gap-0.5">
              <span class="font-bold flex items-center gap-1">
                <span>📊 Luồng 2: Quản lý giám sát & Master Data</span>
              </span>
              <span class="text-[10px] text-slate-400 font-mono">Dashboard MTTR ➔ Tra cứu thiết bị & Phân quyền RBAC</span>
            </button>
          </div>
        </div>

        <!-- Master Hub Portal Link -->
        <div class="mt-3 pt-2 border-t border-slate-800 text-center">
          <a href="../index.html" class="inline-flex items-center gap-1.5 text-[11px] font-mono text-cyan-400 hover:text-cyan-300 font-semibold">
            <span>🌐 Mở Cổng Demo Tổng (index.html)</span>
            <span>→</span>
          </a>
        </div>
      </div>

      <!-- Trigger Floating Button -->
      <button id="smartsop-toggle-panel" class="group flex items-center gap-2 px-3.5 py-2.5 rounded-full bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-mono text-xs font-bold shadow-xl shadow-cyan-900/40 border border-cyan-400/50 transition-all transform hover:scale-105 active:scale-95">
        <span class="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
        <span>⚡ Demo Hub</span>
        <span class="text-[10px] opacity-80 bg-slate-900/60 px-1.5 py-0.5 rounded font-mono">Pills</span>
      </button>
    `;

    document.body.appendChild(widget);

    // Event listeners for widget
    const panel = document.getElementById('smartsop-demo-panel');
    const toggleBtn = document.getElementById('smartsop-toggle-panel');
    const closeBtn = document.getElementById('smartsop-close-panel');

    toggleBtn.onclick = () => panel.classList.toggle('hidden');
    closeBtn.onclick = () => panel.classList.add('hidden');

    // Persona switch buttons
    widget.querySelectorAll('.demo-user-btn').forEach(btn => {
      btn.onclick = () => {
        const userId = btn.getAttribute('data-user');
        setActiveUser(userId);
        showToast(`Đã chuyển sang vai trò: ${DEMO_PERSONAS[userId].role}`, 'success');
        document.getElementById('current-persona-badge').textContent = userId;
      };
    });

    // Scenario 1: SMT Feeder Jam E-204 Flow
    document.getElementById('scenario-1-btn').onclick = () => {
      showToast('Bắt đầu Kịch bản 1: Xử lý sự cố máy SMT E-204...', 'info');
      setTimeout(() => {
        window.location.href = '../ui_2_rag_assistant/code.html?scenario=e204';
      }, 600);
    };

    // Scenario 2: Manager Analytics Flow
    document.getElementById('scenario-2-btn').onclick = () => {
      setActiveUser('ADM-001');
      showToast('Bắt đầu Kịch bản 2: Báo cáo KPI & Master Data...', 'info');
      setTimeout(() => {
        window.location.href = '../ui_5_kpi_dashboard/code.html';
      }, 600);
    };
  }

  // 5. PAGE-SPECIFIC INTERACTIVE LOGIC
  function setupPageInteractions() {
    const page = getCurrentPageName();

    // ==========================================
    // UI 1: LOGIN
    // ==========================================
    if (page === 'ui_1_login') {
      const form = document.getElementById('loginForm');
      if (form) {
        form.onsubmit = function (e) {
          e.preventDefault();
          const staffId = document.getElementById('staffId').value.trim();
          let target = '../ui_2_rag_assistant/code.html';

          if (staffId === 'ADM-001') {
            setActiveUser('ADM-001');
            target = '../ui_5_kpi_dashboard/code.html';
          } else if (staffId === 'OP-412') {
            setActiveUser('OP-412');
            target = '../ui_3_sop_documents/code.html';
          } else {
            setActiveUser('ENG-092');
          }

          const btn = document.getElementById('loginSubmitBtn');
          btn.disabled = true;
          btn.innerHTML = `
            <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span>Xác thực thành công! Đang chuyển hướng...</span>
          `;
          btn.className = btn.className.replace('from-sky-600 to-blue-600', 'bg-emerald-600');

          setTimeout(() => {
            window.location.href = target;
          }, 800);
        };
      }
    }

    // ==========================================
    // UI 2: RAG AI ASSISTANT
    // ==========================================
    if (page === 'ui_2_rag_assistant') {
      // Recent query pill buttons
      const pillsContainer = document.querySelector('.flex.items-center.gap-1\\.5.overflow-x-auto');
      if (pillsContainer) {
        const pillButtons = pillsContainer.querySelectorAll('button');
        const queryMap = ['E-204', 'T-102', 'A-105', 'R-088'];

        pillButtons.forEach((btn, index) => {
          const code = queryMap[index] || 'E-204';
          btn.style.cursor = 'pointer';
          btn.onclick = () => {
            loadQueryTemplate(code);
            showToast(`Đã tải câu hỏi tra cứu mẫu [${code}]`, 'info');
          };
        });
      }

      // Input send button and textarea
      const textarea = document.querySelector('footer textarea');
      const sendBtn = document.querySelector('footer button.bg-gradient-to-r');

      if (sendBtn && textarea) {
        const triggerSend = () => {
          const val = textarea.value.trim();
          if (!val) {
            showToast('Vui lòng nhập câu hỏi hoặc mã lỗi máy!', 'warning');
            return;
          }
          // Detect query code
          let matchedCode = 'E-204';
          if (val.toLowerCase().includes('t-102') || val.toLowerCase().includes('nhiệt độ') || val.toLowerCase().includes('reflow')) matchedCode = 'T-102';
          else if (val.toLowerCase().includes('a-105') || val.toLowerCase().includes('fiducial') || val.toLowerCase().includes('aoi')) matchedCode = 'A-105';
          else if (val.toLowerCase().includes('r-088') || val.toLowerCase().includes('robot') || val.toLowerCase().includes('chân không')) matchedCode = 'R-088';

          simulateAIChat(val, matchedCode);
          textarea.value = '';
        };

        sendBtn.onclick = triggerSend;
        textarea.onkeydown = (e) => {
          if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            triggerSend();
          }
        };
      }

      // "Chọn nhanh mã lỗi máy" button
      const quickCodeBtn = document.querySelector('button:has(.lucide-hash), footer button:last-of-type');
      if (quickCodeBtn) {
        quickCodeBtn.onclick = () => {
          showQuickCodeSelector();
        };
      }

      // Rewire citations buttons
      const citationButtons = document.querySelectorAll('[data-purpose="rag-grounding-citations"] button');
      citationButtons.forEach(btn => {
        btn.onclick = () => {
          window.location.href = '../ui_3_sop_documents/code.html?sop=SOP-SMT-001&page=4';
        };
      });

      // Rewire Action Bar "Tạo phiếu sự cố (Ticket P2)"
      const createTicketBtn = document.querySelector('[data-purpose="response-actions"] button');
      if (createTicketBtn) {
        createTicketBtn.onclick = () => {
          window.location.href = '../ui_4_incident_tickets/code.html?code=E-204';
        };
      }

      // Handle scenario query params
      const urlParams = new URLSearchParams(window.location.search);
      if (urlParams.get('scenario') === 'e204') {
        loadQueryTemplate('E-204');
      }
    }

    // ==========================================
    // UI 3: SOP DOCUMENTS & PDF VIEWER
    // ==========================================
    if (page === 'ui_3_sop_documents') {
      const rows = document.querySelectorAll('main table tbody tr, main .divide-y tr, main div.grid');
      // SOP Table row selection
      const sopTableRows = document.querySelectorAll('table tbody tr');
      if (sopTableRows.length > 0) {
        const sops = ['SOP-SMT-001', 'SOP-REFLOW-02', 'SOP-AOI-003', 'SOP-CLEAN-004'];
        sopTableRows.forEach((row, idx) => {
          row.style.cursor = 'pointer';
          row.onclick = () => {
            const sopCode = sops[idx] || 'SOP-SMT-001';
            updatePdfViewerContent(sopCode);
            showToast(`Đã mở tài liệu: ${sopCode}`, 'info');
          };
        });
      }

      // Live search input filter
      const searchInput = document.getElementById('sop-search-input');
      if (searchInput) {
        searchInput.oninput = () => {
          const q = searchInput.value.toLowerCase().trim();
          sopTableRows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(q) ? '' : 'none';
          });
        };
      }

      // Button: "Trích Xuất Chunk Này Cho AI"
      const extractBtn = document.querySelector('button:has(.fa-robot), button:has(svg), .bg-primary');
      const allButtons = document.querySelectorAll('button');
      allButtons.forEach(btn => {
        if (btn.textContent.includes('Trích Xuất Chunk')) {
          btn.onclick = () => {
            showToast('Đang chuyển chunk văn bản sang Trợ lý AI...', 'success');
            setTimeout(() => {
              window.location.href = '../ui_2_rag_assistant/code.html?query=SOP-SMT-001';
            }, 600);
          };
        }
        if (btn.textContent.includes('Tải lên SOP')) {
          btn.onclick = () => {
            showUploadSopModal();
          };
        }
      });
    }

    // ==========================================
    // UI 4: INCIDENT TICKETS
    // ==========================================
    if (page === 'ui_4_incident_tickets') {
      // "Đã sửa xong ngay qua AI" button
      const resolveAiBtn = document.querySelector('button.bg-emerald-600, button:contains("Đã sửa xong"), button:has(.fa-check)');
      const allBtns = document.querySelectorAll('button');
      allBtns.forEach(btn => {
        if (btn.textContent.includes('Đã sửa xong')) {
          btn.onclick = () => {
            showToast('Đã ghi nhận khắc phục sự cố thành công! MTTR: 2.5 phút.', 'success');
            // Update table row status
            const firstRow = document.querySelector('table tbody tr:first-child');
            if (firstRow) {
              const statusEl = firstRow.querySelector('td:nth-child(5), span.text-amber-400');
              if (statusEl) {
                statusEl.innerHTML = '<span class="text-emerald-400 flex items-center gap-1.5"><span class="w-2 h-2 rounded-full bg-emerald-400"></span>Đã xử lý (MTTR: 2.5m)</span>';
              }
            }
          };
        }
        if (btn.textContent.includes('Xem 4 bước sửa')) {
          btn.onclick = () => {
            window.location.href = '../ui_3_sop_documents/code.html?sop=SOP-SMT-001&page=4';
          };
        }
        if (btn.textContent.includes('+ Báo Sự Cố Mới')) {
          btn.onclick = () => {
            showToast('Form báo sự cố đã sẵn sàng ở bảng bên trái.', 'info');
          };
        }
      });

      // Filter tabs: Tất cả, Đang kiểm tra, Đã giải quyết
      const filterTabs = document.querySelectorAll('button.rounded:has(span), .flex.items-center.gap-1 button');
      // Table filter tabs
      const tabs = document.querySelectorAll('.flex.items-center.bg-\\[\\#0b1326\\] button, button.font-mono');
      tabs.forEach(tab => {
        tab.onclick = () => {
          tabs.forEach(t => t.classList.remove('bg-sky-600', 'text-white'));
          tab.classList.add('bg-sky-600', 'text-white');
          showToast(`Lọc danh sách: ${tab.textContent.trim()}`, 'info');
        };
      });
    }

    // ==========================================
    // UI 5: KPI ANALYTICS DASHBOARD
    // ==========================================
    if (page === 'ui_5_kpi_dashboard') {
      // Top 5 SOP buttons
      const openSopBtns = document.querySelectorAll('button, a');
      openSopBtns.forEach(btn => {
        if (btn.textContent.includes('Mở SOP')) {
          btn.onclick = (e) => {
            e.preventDefault();
            window.location.href = '../ui_3_sop_documents/code.html?sop=SOP-SMT-001';
          };
        }
        if (btn.textContent.includes('Chi tiết SCADA')) {
          btn.onclick = (e) => {
            e.preventDefault();
            window.location.href = '../ui_4_incident_tickets/code.html';
          };
        }
        if (btn.textContent.includes('Xuất Báo Cáo PDF')) {
          btn.onclick = (e) => {
            e.preventDefault();
            showToast('Đang kết xuất báo cáo KPI ISO 9001 ra file PDF...', 'success');
          };
        }
      });
    }

    // ==========================================
    // UI 6: SYSTEM ADMIN
    // ==========================================
    if (page === 'ui_6_system_admin') {
      const allBtns = document.querySelectorAll('button');
      allBtns.forEach(btn => {
        if (btn.textContent.includes('+ Thêm Thiết Bị Mới')) {
          btn.onclick = () => showAddDeviceModal();
        }
        if (btn.textContent.includes('Đồng Bộ Lại DB')) {
          btn.onclick = () => {
            showToast('ChromaDB: Đang tái chỉ mục hóa 148 Chunks Vector...', 'info');
            setTimeout(() => {
              showToast('ChromaDB: 100% Sẵn sàng, HNSW Index đồng bộ.', 'success');
            }, 1200);
          };
        }
        if (btn.textContent.includes('+ Cấp tài khoản')) {
          btn.onclick = () => showAddUserModal();
        }
      });
    }
  }

  // UI 2: Update Chat Content based on template
  function loadQueryTemplate(code) {
    const data = QUERY_TEMPLATES[code] || QUERY_TEMPLATES['E-204'];
    const userQueryText = document.querySelector('[data-purpose="user-query"] p');
    const badgeContainer = document.querySelector('[data-purpose="user-query"] #user-query-badges, [data-purpose="user-query"] .mt-2\\.5, [data-purpose="user-query"] .mt-1\\.5');
    const diagnosisText = document.querySelector('#ai-diagnosis-text, [data-purpose="ai-rag-response"] p.text-slate-300, [data-purpose="ai-rag-response"] div:has(strong) p');
    const sopTitle = document.querySelector('[data-purpose="rag-grounding-citations"] h6');
    const sopCode = document.querySelector('[data-purpose="rag-grounding-citations"] .text-slate-200.font-bold');
    const stepsContainer = document.getElementById('ai-steps-container');

    if (userQueryText) userQueryText.innerHTML = data.question;
    if (badgeContainer) {
      badgeContainer.innerHTML = `
        <span class="px-1.5 py-0.2 rounded bg-sky-950/80 text-sky-300 border border-sky-700/60">${data.badge}</span>
        <span class="px-1.5 py-0.2 rounded bg-sky-950/80 text-sky-300 border border-sky-700/60">${data.device}</span>
        <span class="px-1.5 py-0.2 rounded bg-sky-950/80 text-sky-300 border border-sky-700/60">${data.module}</span>
      `;
    }
    if (diagnosisText) diagnosisText.innerHTML = data.diagnosis;
    if (sopTitle) sopTitle.textContent = data.docDesc;
    if (sopCode) sopCode.textContent = data.targetSop;

    if (stepsContainer && data.steps) {
      stepsContainer.innerHTML = data.steps.map((st, i) => `
        <div class="flex items-start gap-2 p-2 rounded-lg bg-factory-850 border border-slate-700/60 hover:border-slate-600 transition-colors">
          <span class="h-5 w-5 rounded bg-sky-950 border border-sky-600 text-sky-400 flex items-center justify-center font-mono font-bold text-[10px] flex-shrink-0 mt-0.5">
            0${i + 1}
          </span>
          <div class="flex-1 text-[11px] leading-snug">
            <span class="text-slate-200"><strong class="text-slate-100">${st.title}:</strong> ${st.text}</span>
            ${st.required ? '<span class="ml-1 text-[9px] text-emerald-400 bg-emerald-950/60 px-1 py-0.2 rounded border border-emerald-800 font-mono">Bắt buộc</span>' : ''}
          </div>
        </div>
      `).join('');
    }
  }

  // UI 2: Simulate AI Interactive Chat
  function simulateAIChat(question, code) {
    const chatContainer = document.getElementById('chat-conversation-container');
    if (!chatContainer) return;

    const data = QUERY_TEMPLATES[code] || QUERY_TEMPLATES['E-204'];

    // 1. Append User Question Bubble
    const userBubble = document.createElement('div');
    userBubble.className = 'flex items-start gap-3 max-w-4xl ml-auto justify-end animate-fade-in';
    userBubble.innerHTML = `
      <div class="flex flex-col items-end space-y-1.5">
        <div class="flex items-center gap-2">
          <span class="text-[11px] text-slate-400 font-mono">${new Date().toLocaleTimeString()}</span>
          <span class="text-xs font-semibold text-slate-300">${getActiveUser().name}</span>
        </div>
        <div class="bg-gradient-to-r from-sky-900/60 to-blue-900/60 border border-sky-600/40 text-slate-100 p-3.5 rounded-2xl rounded-tr-sm shadow-md text-sm leading-relaxed">
          <p>${question}</p>
        </div>
      </div>
      <div class="w-9 h-9 rounded-lg bg-slate-800 border border-slate-700 flex items-center justify-center flex-shrink-0 text-slate-300 shadow">
        <span class="font-bold text-xs text-sky-400">${getActiveUser().initials}</span>
      </div>
    `;
    chatContainer.appendChild(userBubble);

    // 2. Append Thinking Indicator
    const thinkingBubble = document.createElement('div');
    thinkingBubble.className = 'flex items-start gap-3.5 max-w-5xl animate-pulse';
    thinkingBubble.id = 'ai-thinking-indicator';
    thinkingBubble.innerHTML = `
      <div class="w-9 h-9 rounded-lg bg-cyan-950 border border-cyan-500/50 flex items-center justify-center flex-shrink-0">
        <span class="text-cyan-400 text-xs">AI</span>
      </div>
      <div class="p-3 rounded-xl bg-factory-900 border border-slate-800 text-xs font-mono text-cyan-300 flex items-center gap-2">
        <svg class="animate-spin h-3.5 w-3.5 text-cyan-400" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" class="opacity-25"></circle><path fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" class="opacity-75"></path></svg>
        <span>Đang tìm kiếm ChromaDB (bge-m3) & Gemini RAG Grounding...</span>
      </div>
    `;
    chatContainer.appendChild(thinkingBubble);
    chatContainer.scrollTop = chatContainer.scrollHeight;

    // 3. Replace with Answer
    setTimeout(() => {
      thinkingBubble.remove();
      loadQueryTemplate(code);
      showToast('Đã sinh câu trả lời đối chiếu chuẩn SOP!', 'success');
      chatContainer.scrollTop = chatContainer.scrollHeight;
    }, 1200);
  }

  // Quick Code Selector Modal
  function showQuickCodeSelector() {
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 z-[9999] bg-black/70 backdrop-blur-sm flex items-center justify-center p-4';
    modal.innerHTML = `
      <div class="w-full max-w-md bg-[#0b1326] border border-cyan-500/50 rounded-xl p-5 shadow-2xl text-slate-200">
        <div class="flex items-center justify-between pb-3 border-b border-slate-800">
          <h3 class="text-sm font-bold text-white flex items-center gap-2">
            <span class="text-cyan-400">#</span> Chọn Nhanh Mã Lỗi SMT Thường Gặp
          </h3>
          <button class="text-slate-400 hover:text-white" onclick="this.closest('.fixed').remove()">✕</button>
        </div>
        <div class="mt-3 space-y-2">
          ${Object.keys(QUERY_TEMPLATES).map(k => `
            <div class="p-2.5 rounded-lg bg-[#131b2e] hover:bg-sky-950 border border-slate-700 hover:border-cyan-500/50 cursor-pointer transition-colors" data-code="${k}">
              <div class="flex items-center justify-between font-mono text-xs">
                <span class="font-bold text-cyan-300">${k}</span>
                <span class="text-slate-400">${QUERY_TEMPLATES[k].device}</span>
              </div>
              <p class="text-xs text-slate-300 mt-1">${QUERY_TEMPLATES[k].question}</p>
            </div>
          `).join('')}
        </div>
      </div>
    `;
    document.body.appendChild(modal);

    modal.querySelectorAll('[data-code]').forEach(el => {
      el.onclick = () => {
        const code = el.getAttribute('data-code');
        loadQueryTemplate(code);
        modal.remove();
        showToast(`Đã áp dụng mã lỗi [${code}]`, 'success');
      };
    });
  }

  // UI 3: Update PDF Viewer Content
  function updatePdfViewerContent(sopCode) {
    const sop = SOP_DATABASE[sopCode] || SOP_DATABASE['SOP-SMT-001'];
    const titleEl = document.querySelector('header h1, .font-headline-md, [data-purpose="pdf-header"] h2');
    const pdfFileName = document.querySelector('span:has(.fa-file-pdf), .font-mono.text-sm');

    // Update steps in viewer
    const stepsContainer = document.querySelector('.space-y-4, .space-y-3');
    if (stepsContainer && sop.steps) {
      stepsContainer.innerHTML = sop.steps.map(s => `
        <div class="p-3 rounded-lg bg-surface-container-low border border-outline-variant/30 text-xs">
          <div class="font-bold text-primary font-mono mb-1">BƯỚC ${s.num}:</div>
          <div class="text-on-surface">${s.text}</div>
        </div>
      `).join('');
    }
  }

  // UI 3: Modal Upload SOP
  function showUploadSopModal() {
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 z-[9999] bg-black/70 backdrop-blur-sm flex items-center justify-center p-4';
    modal.innerHTML = `
      <div class="w-full max-w-lg bg-[#0b1326] border border-cyan-500/50 rounded-xl p-6 shadow-2xl text-slate-200">
        <div class="flex items-center justify-between pb-3 border-b border-slate-800">
          <h3 class="text-sm font-bold text-white flex items-center gap-2">
            <span>📄</span> Tải Lên & Xử Lý Tài Liệu SOP Mới (Pipeline Ingestion)
          </h3>
          <button class="text-slate-400 hover:text-white" onclick="this.closest('.fixed').remove()">✕</button>
        </div>
        <div class="mt-4 space-y-3">
          <div class="border-2 border-dashed border-slate-700 hover:border-cyan-400 rounded-lg p-6 text-center cursor-pointer">
            <div class="text-cyan-400 text-3xl mb-2">📁</div>
            <div class="text-xs font-semibold text-white">Kéo thả file PDF SOP hoặc bấm để duyệt file</div>
            <div class="text-[10px] text-slate-500 font-mono mt-1">Hỗ trợ: PDF tối đa 50MB (Bao gồm bảng biểu pdfplumber)</div>
          </div>
          <div class="grid grid-cols-2 gap-3 text-xs">
            <div>
              <label class="block text-[10px] font-mono text-slate-400 mb-1">Mã Quy Trình:</label>
              <input class="w-full bg-[#131b2e] border border-slate-700 rounded p-2 text-white font-mono text-xs" value="SOP-SMT-009" />
            </div>
            <div>
              <label class="block text-[10px] font-mono text-slate-400 mb-1">Dây Chuyền Áp Dụng:</label>
              <select class="w-full bg-[#131b2e] border border-slate-700 rounded p-2 text-white font-mono text-xs">
                <option>Line SMT-01</option>
                <option>Line SMT-02</option>
                <option>Toàn Xưởng</option>
              </select>
            </div>
          </div>
          <div id="upload-progress-container" class="hidden space-y-1.5 pt-2">
            <div class="flex justify-between text-[11px] font-mono">
              <span id="upload-status-text" class="text-cyan-400">Đang trích xuất văn bản & bảng biểu...</span>
              <span id="upload-pct" class="text-white font-bold">45%</span>
            </div>
            <div class="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
              <div id="upload-bar" class="bg-gradient-to-r from-sky-500 to-cyan-400 h-2 rounded-full transition-all duration-300" style="width: 45%"></div>
            </div>
          </div>
        </div>
        <div class="mt-5 flex justify-end gap-2 border-t border-slate-800 pt-3">
          <button class="px-4 py-2 rounded bg-slate-800 hover:bg-slate-700 text-xs font-medium" onclick="this.closest('.fixed').remove()">Hủy</button>
          <button id="start-upload-btn" class="px-4 py-2 rounded bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-xs flex items-center gap-1.5">
            <span>Bắt đầu Ingestion</span>
          </button>
        </div>
      </div>
    `;
    document.body.appendChild(modal);

    document.getElementById('start-upload-btn').onclick = () => {
      const prog = document.getElementById('upload-progress-container');
      const bar = document.getElementById('upload-bar');
      const pct = document.getElementById('upload-pct');
      const status = document.getElementById('upload-status-text');
      prog.classList.remove('hidden');

      let current = 10;
      const interval = setInterval(() => {
        current += 20;
        if (current >= 100) {
          current = 100;
          clearInterval(interval);
          bar.style.width = '100%';
          pct.textContent = '100%';
          status.textContent = 'Vector hóa thành công (BAAI/bge-m3)! Đã lưu vào ChromaDB.';
          setTimeout(() => {
            modal.remove();
            showToast('Tài liệu SOP-SMT-009 đã được chỉ mục hóa vào Vector Store!', 'success');
          }, 800);
        } else {
          bar.style.width = current + '%';
          pct.textContent = current + '%';
          if (current === 50) status.textContent = 'Semantic Chunking 512 tokens...';
          if (current === 70) status.textContent = 'Tạo Vector Embeddings 1024 dims...';
        }
      }, 350);
    };
  }

  // UI 6: Add Device Modal
  function showAddDeviceModal() {
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 z-[9999] bg-black/70 backdrop-blur-sm flex items-center justify-center p-4';
    modal.innerHTML = `
      <div class="w-full max-w-md bg-[#0b1326] border border-cyan-500/50 rounded-xl p-5 shadow-2xl text-slate-200">
        <div class="flex items-center justify-between pb-3 border-b border-slate-800">
          <h3 class="text-sm font-bold text-white flex items-center gap-2">
            <span>⚙️</span> Thêm Thiết Bị Trạm Mới Vào Master Data
          </h3>
          <button class="text-slate-400 hover:text-white" onclick="this.closest('.fixed').remove()">✕</button>
        </div>
        <div class="mt-3 space-y-2.5 text-xs font-mono">
          <div>
            <label class="block text-slate-400 mb-1">Mã Máy Trạm:</label>
            <input class="w-full bg-[#131b2e] border border-slate-700 rounded p-2 text-white" value="MC-SMT-05" />
          </div>
          <div>
            <label class="block text-slate-400 mb-1">Tên & Chủng Loại Thiết Bị:</label>
            <input class="w-full bg-[#131b2e] border border-slate-700 rounded p-2 text-white" value="Yamaha YSM20R Pick & Place" />
          </div>
          <div>
            <label class="block text-slate-400 mb-1">Dây Chuyền:</label>
            <select class="w-full bg-[#131b2e] border border-slate-700 rounded p-2 text-white">
              <option>Dây chuyền SMT-01</option>
              <option>Dây chuyền SMT-02</option>
              <option>Line Kiểm tra QA-01</option>
            </select>
          </div>
        </div>
        <div class="mt-4 pt-3 border-t border-slate-800 flex justify-end gap-2">
          <button class="px-3 py-1.5 rounded bg-slate-800 hover:bg-slate-700 text-xs" onclick="this.closest('.fixed').remove()">Hủy</button>
          <button class="px-3 py-1.5 rounded bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-xs" onclick="this.closest('.fixed').remove(); window.smartsopShowToast('Đã thêm thiết bị MC-SMT-05 vào hệ thống SCADA!', 'success');">Lưu Thiết Bị</button>
        </div>
      </div>
    `;
    document.body.appendChild(modal);
  }

  // UI 6: Add User Modal
  function showAddUserModal() {
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 z-[9999] bg-black/70 backdrop-blur-sm flex items-center justify-center p-4';
    modal.innerHTML = `
      <div class="w-full max-w-md bg-[#0b1326] border border-cyan-500/50 rounded-xl p-5 shadow-2xl text-slate-200">
        <div class="flex items-center justify-between pb-3 border-b border-slate-800">
          <h3 class="text-sm font-bold text-white flex items-center gap-2">
            <span>🛡️</span> Cấp Tài Khoản & Phân Quyền RBAC
          </h3>
          <button class="text-slate-400 hover:text-white" onclick="this.closest('.fixed').remove()">✕</button>
        </div>
        <div class="mt-3 space-y-2.5 text-xs font-mono">
          <div>
            <label class="block text-slate-400 mb-1">Mã Nhân Viên / RFID:</label>
            <input class="w-full bg-[#131b2e] border border-slate-700 rounded p-2 text-white" value="ENG-108" />
          </div>
          <div>
            <label class="block text-slate-400 mb-1">Họ & Tên Kỹ Sư:</label>
            <input class="w-full bg-[#131b2e] border border-slate-700 rounded p-2 text-white" value="Hoàng Minh Đức" />
          </div>
          <div>
            <label class="block text-slate-400 mb-1">Vai Trò (Role):</label>
            <select class="w-full bg-[#131b2e] border border-slate-700 rounded p-2 text-white">
              <option>Kỹ sư trực Line (Engineer)</option>
              <option>Quản trị viên (System Admin)</option>
              <option>Công nhân thao tác (Operator)</option>
            </select>
          </div>
        </div>
        <div class="mt-4 pt-3 border-t border-slate-800 flex justify-end gap-2">
          <button class="px-3 py-1.5 rounded bg-slate-800 hover:bg-slate-700 text-xs" onclick="this.closest('.fixed').remove()">Hủy</button>
          <button class="px-3 py-1.5 rounded bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-xs" onclick="this.closest('.fixed').remove(); window.smartsopShowToast('Đã cấp tài khoản ENG-108 với quyền Shift Engineer!', 'success');">Tạo Tài Khoản</button>
        </div>
      </div>
    `;
    document.body.appendChild(modal);
  }

  // Global export
  window.smartsopShowToast = showToast;
  window.smartsopSetActiveUser = setActiveUser;

  // Initialize when DOM is ready
  function init() {
    rewireNavigationLinks();
    updateUserUI();
    injectFloatingDemoWidget();
    setupPageInteractions();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();

