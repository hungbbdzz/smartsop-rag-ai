import asyncio
import hashlib
import logging
import sys
from pathlib import Path
from pypdf import PdfReader

# Đảm bảo import được app
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from sqlalchemy import select
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.models.production_line import ProductionLine
from app.models.machine import Machine, MachineStatus
from app.models.sop_document import SOPDocument, IngestionStatus

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("seed")


async def seed_data():
    logger.info("🌱 Bắt đầu nạp dữ liệu mẫu khởi tạo (Seed Data)...")

    async with AsyncSessionLocal() as session:
        # 1. NẠP TÀI KHOẢN NGƯỜI DÙNG (4 ROLES)
        users_data = [
            {
                "username": "admin",
                "full_name": "System Administrator (Quản trị hệ thống)",
                "email": "admin@smartsop.factory",
                "role": UserRole.ADMIN,
                "password": hash_password("Admin@2026"),
            },
            {
                "username": "manager",
                "full_name": "Trần Quản Đốc (Giám đốc Xưởng SMT)",
                "email": "manager.smt@smartsop.factory",
                "role": UserRole.FACTORY_MANAGER,
                "password": hash_password("Manager@2026"),
            },
            {
                "username": "engineer",
                "full_name": "Lê Kỹ Sư (Kỹ sư Trưởng ca 1)",
                "email": "engineer.shift1@smartsop.factory",
                "role": UserRole.SHIFT_ENGINEER,
                "password": hash_password("Engineer@2026"),
            },
            {
                "username": "operator",
                "full_name": "Phạm Công Nhân (Công nhân đứng máy)",
                "email": "operator.op412@smartsop.factory",
                "role": UserRole.OPERATOR,
                "password": hash_password("Operator@2026"),
            },
        ]

        user_map = {}
        for u_info in users_data:
            stmt = select(User).where(User.username == u_info["username"])
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            if not user:
                user = User(
                    username=u_info["username"],
                    full_name=u_info["full_name"],
                    email=u_info["email"],
                    role=u_info["role"],
                    password_hash=u_info["password"],
                    is_active=True,
                )
                session.add(user)
                await session.flush()
                logger.info(f"  + Tạo tài khoản: {user.username} ({user.role.value})")
            else:
                logger.info(f"  - Tài khoản đã tồn tại: {user.username}")
            user_map[u_info["username"]] = user

        # 2. NẠP DÂY CHUYỀN SẢN XUẤT (PRODUCTION LINES)
        lines_data = [
            {
                "name": "Dây chuyền SMT-01 (High-Speed)",
                "factory_zone": "Xưởng A - Tầng 2",
                "description": "Dây chuyền dán bề mặt tốc độ cao chuyên sản xuất bo mạch điện thoại",
            },
            {
                "name": "Dây chuyền SMT-02 (Flexible)",
                "factory_zone": "Xưởng A - Tầng 2",
                "description": "Dây chuyền linh hoạt phục vụ sản xuất module IoT và phụ tùng ô tô",
            },
        ]

        line_map = {}
        for l_info in lines_data:
            stmt = select(ProductionLine).where(ProductionLine.name == l_info["name"])
            result = await session.execute(stmt)
            line = result.scalar_one_or_none()
            if not line:
                line = ProductionLine(
                    name=l_info["name"],
                    factory_zone=l_info["factory_zone"],
                    description=l_info["description"],
                )
                session.add(line)
                await session.flush()
                logger.info(f"  + Tạo dây chuyền: {line.name}")
            else:
                logger.info(f"  - Dây chuyền đã tồn tại: {line.name}")
            line_map[l_info["name"]] = line

        # 3. NẠP MÁY MÓC THIẾT BỊ (MACHINES)
        line1 = line_map["Dây chuyền SMT-01 (High-Speed)"]
        line2 = line_map["Dây chuyền SMT-02 (Flexible)"]

        machines_data = [
            {
                "machine_code": "SMT-FUJI-01",
                "name": "Máy gắp chíp tốc độ cao Fuji NXT III",
                "model": "NXT-III M6",
                "manufacturer": "Fuji Corporation (Japan)",
                "status": MachineStatus.OPERATIONAL,
                "line_id": line1.id,
            },
            {
                "machine_code": "REFLOW-HELLER-01",
                "name": "Lò hàn hồi lưu Heller 9 vùng nhiệt",
                "model": "Heller 1809 MK5",
                "manufacturer": "Heller Industries (USA)",
                "status": MachineStatus.OPERATIONAL,
                "line_id": line1.id,
            },
            {
                "machine_code": "AOI-KOHYOUNG-01",
                "name": "Hệ thống kiểm tra quang học 3D AOI",
                "model": "Zenith 3D AOI",
                "manufacturer": "Koh Young Technology",
                "status": MachineStatus.OPERATIONAL,
                "line_id": line1.id,
            },
            {
                "machine_code": "SMT-AIMEX-02",
                "name": "Máy gắp linh kiện đa năng Fuji AIMEX",
                "model": "AIMEX IIIc",
                "manufacturer": "Fuji Corporation (Japan)",
                "status": MachineStatus.MAINTENANCE,
                "line_id": line2.id,
            },
            {
                "machine_code": "SPI-PARMI-01",
                "name": "Máy soi kem hàn 3D SPI Parmi",
                "model": "SIGMA X SPI",
                "manufacturer": "Parmi Corp",
                "status": MachineStatus.OPERATIONAL,
                "line_id": line2.id,
            },
        ]

        machine_map = {}
        for m_info in machines_data:
            stmt = select(Machine).where(Machine.machine_code == m_info["machine_code"])
            result = await session.execute(stmt)
            machine = result.scalar_one_or_none()
            if not machine:
                machine = Machine(
                    machine_code=m_info["machine_code"],
                    name=m_info["name"],
                    model=m_info["model"],
                    manufacturer=m_info["manufacturer"],
                    status=m_info["status"],
                    line_id=m_info["line_id"],
                )
                session.add(machine)
                await session.flush()
                logger.info(f"  + Tạo máy móc: {machine.machine_code} - {machine.name}")
            else:
                logger.info(f"  - Máy móc đã tồn tại: {machine.machine_code}")
            machine_map[m_info["machine_code"]] = machine

        # 4. NẠP METADATA TÀI LIỆU SOP MẪU
        admin_user = user_map["admin"]
        fuji_machine = machine_map["SMT-FUJI-01"]
        reflow_machine = machine_map["REFLOW-HELLER-01"]
        aoi_machine = machine_map["AOI-KOHYOUNG-01"]

        sops_data = [
            {
                "document_code": "SOP-SMT-001-VN",
                "title": "Quy trình Xử lý Sự cố & Căn chỉnh Đầu hút Máy Gắp SMT Fuji NXT III",
                "file_name": "SOP_SMT_001_Pick_And_Place_Machine_Troubleshooting.pdf",
                "line_id": line1.id,
                "machine_id": fuji_machine.id,
                "version": "1.0",
                "chunk_count": 28,
                "ingestion_status": IngestionStatus.COMPLETED,
            },
            {
                "document_code": "SOP-REFLOW-002-VN",
                "title": "Quy trình Kiểm soát Khuyết tật & Hồ sơ Nhiệt độ Lò Hàn Hồi lưu Reflow",
                "file_name": "SOP_REFLOW_002_Reflow_Soldering_Defects_Remedies.pdf",
                "line_id": line1.id,
                "machine_id": reflow_machine.id,
                "version": "1.1",
                "chunk_count": 35,
                "ingestion_status": IngestionStatus.COMPLETED,
            },
            {
                "document_code": "SOP-AOI-003-VN",
                "title": "Tiêu chuẩn Đánh giá Lỗi Quang học Tự động 3D AOI (IPC-A-610G)",
                "file_name": "SOP_AOI_003_Automated_Optical_Inspection_Standards.pdf",
                "line_id": line1.id,
                "machine_id": aoi_machine.id,
                "version": "1.0",
                "chunk_count": 31,
                "ingestion_status": IngestionStatus.COMPLETED,
            },
        ]

        for s_info in sops_data:
            # Tự động đọc file PDF thật từ thư mục sops để lấy hash SHA-256 và số trang chính xác 100%
            pdf_path = settings.SOPS_SAMPLE_DIR / s_info["file_name"]
            if pdf_path.exists():
                file_bytes = pdf_path.read_bytes()
                real_hash = hashlib.sha256(file_bytes).hexdigest()
                real_size = len(file_bytes)
                reader = PdfReader(pdf_path)
                real_pages = len(reader.pages)
                clean_file_path = f"data/sops/{s_info['file_name']}"
            else:
                real_hash = "mock_hash_fallback"
                real_size = 0
                real_pages = 1
                clean_file_path = f"data/sops/{s_info['file_name']}"

            stmt = select(SOPDocument).where(SOPDocument.document_code == s_info["document_code"])
            result = await session.execute(stmt)
            sop = result.scalar_one_or_none()
            if not sop:
                sop = SOPDocument(
                    document_code=s_info["document_code"],
                    title=s_info["title"],
                    file_name=s_info["file_name"],
                    file_path=clean_file_path,
                    file_hash=real_hash,
                    file_size=real_size,
                    line_id=s_info["line_id"],
                    machine_id=s_info["machine_id"],
                    uploaded_by=admin_user.id,
                    version=s_info["version"],
                    page_count=real_pages,
                    chunk_count=s_info["chunk_count"],
                    ingestion_status=s_info["ingestion_status"],
                )
                session.add(sop)
                logger.info(f"  + Tạo tài liệu SOP: {sop.document_code} ({real_pages} trang, hash: {real_hash[:12]}...)")
            else:
                # Tự động cập nhật metadata thật nếu trước đó lưu dữ liệu giả
                sop.file_hash = real_hash
                sop.file_size = real_size
                sop.page_count = real_pages
                sop.file_path = clean_file_path
                logger.info(f"  - Cập nhật metadata SOP thật: {sop.document_code} ({real_pages} trang, hash: {real_hash[:12]}...)")

        await session.commit()
        logger.info("✅ Nạp dữ liệu mẫu hoàn tất 100%!")


if __name__ == "__main__":
    asyncio.run(seed_data())

