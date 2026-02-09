# NagaCheck - Database Maintenance Tool

Aplikasi Python untuk **Database Maintenance**: Check, Repair, dan Optimize tabel MySQL, dengan **Web Interface** modern menggunakan Flask.

## Status Project

✅ **NAGACHECK v2.0.0** - Professional Database Maintenance Tool

### Design & Branding
- 🎨 **Color Scheme**: Soft Orange, Warm Gray, White (NGTC Corporate Colors)
- 🏢 **Branding**: Nagatech Sistem Integrator (NGTC)
- 🎯 **UI/UX**: Modern, Clean, Easy on the Eyes
- 🖼️ **Logo**: NGTC Logo displayed in header (see [Logo Setup](#logo-setup))

### Versi Terkini
- **Versi**: 2.0.0 (Flask Web Interface)
- **Build Date**: February 2026
- **Executable**: `dist/nagacheck.exe` (Windows standalone dengan auto-open browser)
- **Platform**: Cross-platform (Windows, Linux, macOS)

### Database Support
- ✅ MySQL 5.0.51b-community-nt-log (AppServ)
- ✅ MySQL 5.x - 8.x
- ✅ Charset: UTF8
- ✅ Authentication: mysql_native_password

## Fitur

### Core Features - Database Maintenance
- ✅ **CHECK TABLE** - Deteksi tabel corrupt atau error
- ✅ **REPAIR TABLE** - Otomatis repair tabel yang bermasalah
- ✅ **OPTIMIZE TABLE** - Optimize semua tabel untuk performa maksimal
- ✅ **Table Selection** - User bisa pilih tabel mana yang ingin di-check (default: all)
- ✅ **Batch Processing** - Check multiple tables sekaligus
- ✅ **Real-time Results** - Lihat status check/repair/optimize per table

### User Interface
- ✅ **Web-based Interface** - Modern UI menggunakan Flask + Bootstrap 5
- ✅ **Auto-open Browser** - Otomatis membuka browser saat exe dijalankan
- ✅ Koneksi ke database MySQL dengan PyMySQL driver
- ✅ **Real-time Progress Bar** dengan AJAX updates
- ✅ **Responsive Design** - Bisa diakses dari desktop, tablet, atau mobile
- ✅ **Test Connection** button untuk validasi database
- ✅ **Load Tables** button untuk preview tabel dan info (rows, size)
- ✅ **Select All / Deselect All** untuk mudah pilih tabel
- ✅ **Hasil Maintenance** ditampilkan dalam table dengan badge status
- ✅ **Password visibility toggle** untuk keamanan
- ✅ Enter key navigation antar textbox

### Data Processing
- ✅ Safe type conversion (float, int) dengan fallback ke 0
- ✅ String trimming untuk semua value
- ✅ Date conversion ke ISO 8601 format
- ✅ Handle empty/null/dash values

### Actions Performed
1. **CHECK TABLE** - MySQL command untuk cek struktur tabel
   - Deteksi corrupt files
   - Deteksi index errors
   - Validasi table integrity

2. **REPAIR TABLE** (jika diperlukan)
   - Otomatis repair jika CHECK menemukan error
   - Support untuk MyISAM dan InnoDB tables
   - Restore data yang corrupted

3. **OPTIMIZE TABLE** (selalu dijalankan)
   - Defragment table data
   - Reclaim unused space
   - Update table statistics
   - Improve query performance

### Maintenance Log
- ✅ Generate `maintenance_log.txt` di folder `data/`
- ✅ Detail per table: status, action, result
- ✅ Summary: total tables checked, repaired, optimized
- ✅ Auto-open folder setelah maintenance selesai

## Logo Setup

### Menambahkan Logo NGTC ke Aplikasi

Untuk menampilkan logo Nagatech Sistem Integrator di header aplikasi:

1. **Siapkan File Logo**
   - Format: PNG (dengan background transparan lebih baik)
   - Ukuran: Tinggi 50-100px (width auto)
   - Nama file: `ngtc-logo.png`

2. **Lokasi Penyimpanan**
   ```
   static/images/ngtc-logo.png
   ```

3. **Copy Logo**
   ```bash
   # Windows
   copy /path/to/your/logo.png static/images/ngtc-logo.png
   
   # Linux/Mac
   cp /path/to/your/logo.png static/images/ngtc-logo.png
   ```

4. **Verifikasi**
   - Refresh browser (F5)
   - Logo akan muncul di header dengan background putih dan shadow effect

**Catatan**: Aplikasi akan tetap berjalan normal jika logo tidak ditemukan (tidak akan error).

## Instalasi

### Opsi 1: Executable / EXE (Recommended)
1. Download `nagacheck.exe` dari folder `dist/`
2. Double-click untuk menjalankan
3. **Browser akan otomatis terbuka** ke http://localhost:5000
4. Tidak perlu install Python atau dependencies
5. Console window akan tetap terbuka (menampilkan server logs)

### Opsi 2: Dari Source Code
1. Pastikan Python 3.13+ sudah terinstall
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Jalankan aplikasi:
   ```bash
   python app.py
   ```
4. Browser akan otomatis terbuka ke http://localhost:5000

### Opsi 3: Manual Browser Access
Jika browser tidak otomatis terbuka:
- Buka browser manual
- Ketik: `http://localhost:5000`
- Aplikasi siap digunakan

## Cara Penggunaan

### 1. Koneksi Database
Isi konfigurasi database di form:
- **IP / Host**: Alamat server MySQL (contoh: localhost, 127.0.0.1)
- **USER**: Username MySQL (contoh: root)
- **PASSWORD**: Password MySQL (klik icon mata untuk show/hide)
- **DATABASE**: Nama database yang ingin di-maintenance

*Tips: Gunakan Enter untuk navigasi cepat antar field*

### 2. Test Connection (Optional)
Klik tombol **Test Connection** untuk:
- Validasi kredensial database
- Cek versi MySQL
- Hitung jumlah tabel yang tersedia

### 3. Load Tables
1. Klik tombol **Load Tables**
2. Aplikasi akan menampilkan semua tabel dengan info:
   - Nama tabel
   - Jumlah rows
   - Size (MB/KB)
3. **Default: Semua tabel ter-check (selected)**

### 4. Select Tables (Optional)
Anda bisa:
- **Select All**: Check semua tabel
- **Deselect All**: Uncheck semua tabel
- **Manual Selection**: Klik checkbox individual per tabel
- **Check All Checkbox**: Check di header untuk toggle all

### 5. Start Maintenance
1. Klik tombol **START MAINTENANCE**
2. Progress bar akan menampilkan:
   - Persentase progress (0-100%)
   - Counter: Current / Total tables
   - Status message: "Checking: table_name"
3. Tunggu hingga proses selesai

### 6. Lihat Hasil
1. **Hasil ditampilkan di halaman** dalam bentuk table:
   - Table Name
   - Status (OK/ERROR badge)
   - Action (None/REPAIR/OPTIMIZE/REPAIR+OPTIMIZE)
   - Result (Healthy/Repaired/Optimized)
2. Klik tombol **OPEN LOG FOLDER** untuk buka folder `data/`
3. Cek file `maintenance_log.txt` untuk detail lengkap

## Output Files

File hasil maintenance disimpan di folder `data/`:

### Maintenance Log
`maintenance_log.txt` berisi:
- Date & time maintenance
- Database name
- Table-by-table report:
  - Table Name
  - Status (OK/ERROR)
  - Action Taken (None/REPAIR/OPTIMIZE/REPAIR+OPTIMIZE)
  - Result (Healthy/Repaired/Optimized/Failed)
- Summary statistics:
  - Total tables checked
  - Tables with issues
  - Tables repaired
  - Tables optimized

### Log Format Example
```
================================================================================
DATABASE MAINTENANCE LOG
================================================================================
Date: 2026-02-08 15:30:00
Database: db_nagagold
================================================================================

Table Name                     Status          Action               Result
------------------------------------------------------------------------------------
tm_kelompok                    OK              OPTIMIZE             Optimized
tm_barang                      ERROR           REPAIR + OPTIMIZE    Repaired & Optimized  
tm_sales                       OK              OPTIMIZE             Optimized
------------------------------------------------------------------------------------
Total tables checked: 3
Tables with issues: 1
Tables repaired: 1
Tables optimized: 3
================================================================================
```

## Build Executable

### Build NagaCheck v2.0
Untuk membuat file .exe:
```bash
py -m PyInstaller --clean nagacheck.spec
```

Atau gunakan batch file:
```bash
build_nagacheck.bat
```

### Output
- Executable akan tersimpan di folder `dist/`
- File `nagacheck.exe` siap didistribusikan
- Size: ~20-25 MB (include Flask + PyMySQL + templates + static files)

## Troubleshooting

### Browser Tidak Auto-Open
- ✅ Tunggu 2-3 detik setelah exe berjalan
- ✅ Buka browser manual ke `http://localhost:5000`
- ✅ Pastikan port 5000 tidak digunakan aplikasi lain

### Error Koneksi Database
- ✅ Pastikan MySQL service running
- ✅ Cek username/password benar
- ✅ Database sudah ada di MySQL
- ✅ Gunakan tombol "Test Connection" untuk validasi
- ✅ User MySQL harus punya privilege: SELECT, REPAIR, OPTIMIZE

### Tables Tidak Muncul Setelah Load
- ✅ Pastikan database tidak kosong
- ✅ Refresh browser (F5)
- ✅ Cek permission user di MySQL
- ✅ Test connection dulu sebelum load tables

### Repair Table Gagal
- ✅ **InnoDB Tables**: `innodb_force_recovery` mungkin perlu diset
- ✅ **MyISAM Tables**: Pastikan file .MYI dan .MYD tidak corrupt
- ✅ Check MySQL error log untuk detail
- ✅ User harus punya privilege REPAIR TABLE

### Optimize Tidak Berpengaruh
- ✅ Normal untuk InnoDB tables dengan data sedikit
- ✅ Benefit optimize terlihat di table besar (>1GB)
- ✅ Run optimize di off-peak hours untuk production

### Port 5000 Already in Use
Jika port 5000 sudah dipakai:
```python
# Edit app.py, ganti port 5000 ke port lain (misal 5001)
app.run(host='localhost', port=5001, debug=False)
```

### Console Window Tertutup
Jangan close console window! Flask server berjalan di console:
- ✅ Console menampilkan server logs
- ✅ Minimize saja jika mengganggu
- ✅ Close console = server berhenti

### File .exe tidak jalan
- ✅ Pastikan tidak ada antivirus yang block
- ✅ Run as Administrator jika perlu
- ✅ Ekstrak ke folder dengan path tanpa spasi/karakter spesial

### Browser Menampilkan "Cannot Connect"
- ✅ Pastikan Flask server masih berjalan (cek console window)
- ✅ Refresh browser (F5)
- ✅ Clear browser cache
- ✅ Coba browser lain (Chrome, Firefox, Edge)

## Struktur Project

```
NagaCheck/
├── dist/
│   └── nagacheck.exe             # Executable siap pakai (CURRENT)
├── data/                          # Output folder (auto-created)
│   └── maintenance_log.txt        # Log hasil check/repair/optimize
├── templates/                     # Flask HTML templates
│   └── index.html                 # Main UI page
├── static/                        # Static assets
│   ├── css/
│   │   └── style.css              # Custom styles
│   ├── js/
│   │   └── app.js                 # Frontend JavaScript
│   └── images/
│       ├── ngtc-logo.png          # NGTC Logo (add your logo here)
│       └── README_LOGO.md         # Logo instructions
├── app.py                         # Flask application (MAIN)
├── nagacheck.spec                # PyInstaller spec
├── build_nagacheck.bat           # Build script
├── requirements.txt               # Python dependencies
├── .gitignore                     # Git ignore rules
└── README.md                      # Dokumentasi
```

## Teknologi yang Digunakan

### Backend
- **Python 3.13**: Bahasa pemrograman
- **Flask 3.0.0**: Web framework
- **Werkzeug 3.0.1**: WSGI utility library
- **PyMySQL 1.1.2**: MySQL driver (kompatibel MySQL 5.x - 8.x)

### Frontend
- **Bootstrap 5.3.0**: CSS framework
- **Bootstrap Icons**: Icon library
- **Vanilla JavaScript**: Frontend logic (no jQuery)
- **AJAX/Fetch API**: Asynchronous requests

### Design System & Color Palette
- **Primary Orange**: `#FF9A56` (Soft, Warm Orange)
- **Dark Orange**: `#FF8C42` (Hover states, Accents)
- **Light Orange**: `#FFB074` (Highlights, Gradients)
- **Dark Gray**: `#2C3E50` (Text, Headers)
- **Medium Gray**: `#546E7A` (Secondary text)
- **Light Gray**: `#ECEFF1` (Backgrounds, Borders)
- **Background**: Soft gradient `#F5F7FA → #E8EAF6`
- **Card Background**: White with 95% opacity + backdrop blur
- **Shadows**: Subtle orange-tinted shadows (`rgba(255, 154, 86, 0.15)`)

**Design Principles**:
- 🎨 Soft, warm colors (easy on the eyes)
- 🌈 Smooth gradients and transitions
- ✨ Modern glassmorphism effects
- 🎯 High readability with proper contrast
- 🏢 Corporate branding (NGTC colors)
- 📱 Responsive design

### Database Maintenance Commands
- **CHECK TABLE**: MySQL command untuk cek table integrity
- **REPAIR TABLE**: MySQL command untuk repair corrupted tables
- **OPTIMIZE TABLE**: MySQL command untuk defragment & optimize
- **SHOW TABLE STATUS**: Untuk ambil table info (rows, size)

### Build & Packaging
- **PyInstaller 6.16.0**: Executable builder
- **Auto-browser**: webbrowser module (Python stdlib)
- **Threading**: Timer untuk auto-open browser

## Database Requirements

### MySQL Version Support
- ✅ MySQL 5.0.x - 8.0.x
- ✅ MariaDB 10.x
- ✅ Percona Server

### Required MySQL Privileges
User yang digunakan harus punya privilege:
```sql
GRANT SELECT, INSERT, UPDATE, DELETE, 
      CREATE, DROP, INDEX, ALTER,
      LOCK TABLES, EXECUTE,
      -- Untuk maintenance:
      REPAIR, OPTIMIZE
ON database_name.* TO 'username'@'localhost';
```

### Supported Table Engines
- ✅ **MyISAM**: Full support (CHECK, REPAIR, OPTIMIZE)
- ✅ **InnoDB**: Full support (CHECK, OPTIMIZE, REPAIR dengan batasan)
- ⚠️ **MEMORY**: Optimize only (tidak support REPAIR)
- ⚠️ **CSV**: Limited support

### Connection Info
- **Host**: localhost atau IP address
- **Port**: 3306 (default MySQL)
- **Charset**: utf8 atau utf8mb4
- **Authentication**: mysql_native_password

## Use Cases

### Kapan Harus Jalankan Maintenance?

1. **Rutin/Scheduled** (Recommended):
   - Jalankan seminggu sekali di off-peak hours
   - Optimize semua tabel untuk performa optimal
   - Preventive maintenance

2. **Setelah Bulk Operations**:
   - Setelah import data besar
   - Setelah delete banyak records
   - Setelah update massive

3. **Database Performance Issues**:
   - Query jadi lambat
   - Table fragmentation tinggi
   - Disk space tidak berkurang setelah delete

4. **Error/Corrupt Detection**:
   - MySQL error "Table is marked as crashed"
   - "Can't open file" errors
   - Inconsistent query results

5. **Post-Crash Recovery**:
   - Setelah server crash
   - Setelah power failure
   - Setelah force shutdown

## Contributors

Developed by: Nagatech SI Team

## Lisensi

Aplikasi ini dibuat untuk keperluan database maintenance.

---

## Quick Start Guide

```bash
# 1. Download & Extract
# Download nagacheck.exe

# 2. Run
# Double-click nagacheck.exe

# 3. Browser akan auto-open

# 4. Input database credentials

# 5. Click "Load Tables"

# 6. Select tables yang ingin di-check (default: all selected)

# 7. Click "START MAINTENANCE"

# 8. Wait & see results!
```

## FAQ

**Q: Apakah aman untuk production database?**  
A: Ya, tapi disarankan:
- Backup database dulu
- Jalankan di off-peak hours
- Test di development environment dulu

**Q: Berapa lama prosesnya?**  
A: Tergantung jumlah dan size tabel:
- < 10 tables, <1GB: ~1-2 menit
- 10-50 tables, 1-10GB: ~5-10 menit
- \> 50 tables, \>10GB: ~15-30 menit

**Q: Bisa di schedule otomatis?**  
A: Bisa dengan Windows Task Scheduler atau cron (Linux), tapi perlu modifikasi untuk batch mode (non-interactive).

**Q: Support untuk remote MySQL server?**  
A: Ya, tinggal ganti Host dengan IP remote server. Pastikan port 3306 terbuka dan user punya akses dari IP Anda.

**Q: Apakah data bisa hilang?**  
A: Tidak, CHECK/REPAIR/OPTIMIZE tidak delete data. Tapi tetap disarankan backup dulu untuk keamanan.

**Q: Bisa untuk PostgreSQL atau SQL Server?**  
A: Tidak, tool ini khusus untuk MySQL/MariaDB saja.

---

**Need Help?** Contact Nagatech SI Team# nagacageur
