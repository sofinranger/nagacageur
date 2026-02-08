"""
Flask Database Maintenance Tool - Web-based Interface
Check, Repair, and Optimize MySQL Tables
Auto-opens browser on startup
"""
from flask import Flask, render_template, request, jsonify, Response, stream_with_context
import json
from datetime import datetime
import os
import sys
import subprocess
import webbrowser
from threading import Timer
import pymysql
from pymysql import Error as PyMySQLError

app = Flask(__name__)
app.config['SECRET_KEY'] = 'nagagold-db-maintenance-2026'

# MySQL Configuration
MYSQL_AVAILABLE = True
MYSQL_DRIVER = 'pymysql'

# Global variables for progress tracking
maintenance_status = {
    'is_running': False,
    'current': 0,
    'total': 0,
    'percentage': 0,
    'message': '',
    'completed': False,
    'error': None,
    'results': []
}

check_results = []


def connect_to_mysql(host, user, password, database):
    """Establish connection to MySQL database"""
    try:
        print(f"[LOG] Attempting to connect to MySQL database...")
        print(f"[LOG] Host: {host}")
        print(f"[LOG] User: {user}")
        print(f"[LOG] Database: {database}")
        
        connection = pymysql.connect(
            host=host,
            port=3306,
            user=user,
            password=password,
            database=database,
            charset='utf8',
            connect_timeout=10,
            cursorclass=pymysql.cursors.DictCursor
        )
        
        if connection.open:
            cursor = connection.cursor()
            cursor.execute("SELECT VERSION()")
            db_info = cursor.fetchone()
            version = list(db_info.values())[0] if db_info else "Unknown"
            cursor.close()
            
            print(f"[LOG] ✓ Connection successful!")
            print(f"[LOG] MySQL Server version: {version}")
            print(f"[LOG] Connected to database: {database}")
            return connection
            
    except Exception as e:
        print(f"[LOG] ✗ Connection failed: {str(e)}")
        raise e


def check_table(connection, table_name):
    """Check table for errors"""
    try:
        cursor = connection.cursor()
        cursor.execute(f"CHECK TABLE `{table_name}`")
        result = cursor.fetchall()
        cursor.close()
        return result
    except Exception as e:
        print(f"[LOG] Error checking table {table_name}: {str(e)}")
        return [{'Msg_type': 'error', 'Msg_text': str(e)}]


def repair_table(connection, table_name):
    """Repair corrupted table"""
    try:
        cursor = connection.cursor()
        cursor.execute(f"REPAIR TABLE `{table_name}`")
        result = cursor.fetchall()
        cursor.close()
        return result
    except Exception as e:
        print(f"[LOG] Error repairing table {table_name}: {str(e)}")
        return [{'Msg_type': 'error', 'Msg_text': str(e)}]


def optimize_table(connection, table_name):
    """Optimize table"""
    try:
        cursor = connection.cursor()
        cursor.execute(f"OPTIMIZE TABLE `{table_name}`")
        result = cursor.fetchall()
        cursor.close()
        return result
    except Exception as e:
        print(f"[LOG] Error optimizing table {table_name}: {str(e)}")
        return [{'Msg_type': 'error', 'Msg_text': str(e)}]


def get_table_status(connection, table_name):
    """Get table status information"""
    try:
        cursor = connection.cursor()
        cursor.execute(f"SHOW TABLE STATUS LIKE '{table_name}'")
        result = cursor.fetchone()
        cursor.close()
        return result
    except Exception as e:
        print(f"[LOG] Error getting table status {table_name}: {str(e)}")
        return None


def save_maintenance_log(results, database_name):
    """Save maintenance log file"""
    try:
        data_folder = "data"
        if not os.path.exists(data_folder):
            os.makedirs(data_folder)
        
        log_file = os.path.join(data_folder, "maintenance_log.txt")
        
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("=" * 100 + "\n")
            f.write("DATABASE MAINTENANCE LOG\n")
            f.write("=" * 100 + "\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Database: {database_name}\n")
            f.write("=" * 100 + "\n\n")
            
            f.write(f"{'Table Name':<30} {'Status':<15} {'Action':<20} {'Result':<30}\n")
            f.write("-" * 100 + "\n")
            
            for result in results:
                f.write(f"{result['table']:<30} {result['status']:<15} {result['action']:<20} {result['result']:<30}\n")
            
            f.write("-" * 100 + "\n")
            f.write(f"Total tables checked: {len(results)}\n")
            f.write(f"Tables with issues: {sum(1 for r in results if r['action'] != 'None')}\n")
            f.write(f"Tables repaired: {sum(1 for r in results if 'REPAIR' in r['action'])}\n")
            f.write(f"Tables optimized: {sum(1 for r in results if 'OPTIMIZE' in r['action'])}\n")
            f.write("=" * 100 + "\n")
        
        print(f"\n[LOG] Maintenance log saved to: {log_file}")
        
    except Exception as e:
        print(f"[LOG] Error saving maintenance log: {str(e)}")


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/get-tables', methods=['POST'])
def get_tables():
    """Get list of all tables in database"""
    try:
        data = request.get_json()
        host = data.get('host', '').strip()
        user = data.get('user', '').strip()
        password = data.get('password', '').strip()
        database = data.get('database', '').strip()
        
        if not all([host, user, database]):
            return jsonify({
                'success': False,
                'message': 'Please fill in Host, User, and Database fields!'
            })
        
        connection = connect_to_mysql(host, user, password, database)
        
        if connection:
            cursor = connection.cursor()
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            table_list = []
            for table_row in tables:
                table_name = list(table_row.values())[0]
                
                # Get table info
                status = get_table_status(connection, table_name)
                rows = status.get('Rows', 0) if status else 0
                size = status.get('Data_length', 0) if status else 0
                
                # Format size
                if size > 1024 * 1024:
                    size_str = f"{size / (1024 * 1024):.2f} MB"
                elif size > 1024:
                    size_str = f"{size / 1024:.2f} KB"
                else:
                    size_str = f"{size} B"
                
                table_list.append({
                    'name': table_name,
                    'rows': rows,
                    'size': size_str
                })
            
            cursor.close()
            connection.close()
            
            return jsonify({
                'success': True,
                'tables': table_list
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Connection failed. Please check your credentials.'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })


@app.route('/test-connection', methods=['POST'])
def test_connection():
    """Test MySQL connection"""
    try:
        data = request.get_json()
        host = data.get('host', '').strip()
        user = data.get('user', '').strip()
        password = data.get('password', '').strip()
        database = data.get('database', '').strip()
        
        if not all([host, user, database]):
            return jsonify({
                'success': False,
                'message': 'Please fill in Host, User, and Database fields!'
            })
        
        connection = connect_to_mysql(host, user, password, database)
        
        if connection:
            cursor = connection.cursor()
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            table_count = len(tables)
            
            cursor.execute("SELECT VERSION()")
            version_data = cursor.fetchone()
            version = list(version_data.values())[0] if version_data else "Unknown"
            
            cursor.close()
            connection.close()
            
            return jsonify({
                'success': True,
                'message': f'✓ Connected successfully!\nMySQL: {version}\nTables: {table_count}'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Connection failed. Please check your credentials.'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })


@app.route('/start-maintenance', methods=['POST'])
def start_maintenance():
    """Start table check/repair/optimize process"""
    global maintenance_status, check_results
    
    try:
        data = request.get_json()
        host = data.get('host', '').strip()
        user = data.get('user', '').strip()
        password = data.get('password', '').strip()
        database = data.get('database', '').strip()
        selected_tables = data.get('tables', [])
        
        if not all([host, user, database]):
            return jsonify({
                'success': False,
                'message': 'Please fill in all required fields!'
            })
        
        if not selected_tables:
            return jsonify({
                'success': False,
                'message': 'Please select at least one table to check!'
            })
        
        # Reset status
        maintenance_status = {
            'is_running': True,
            'current': 0,
            'total': len(selected_tables),
            'percentage': 0,
            'message': 'Connecting to database...',
            'completed': False,
            'error': None,
            'results': []
        }
        check_results = []
        
        # Connect to database
        connection = connect_to_mysql(host, user, password, database)
        
        if not connection:
            maintenance_status['error'] = 'Connection failed'
            maintenance_status['is_running'] = False
            return jsonify({
                'success': False,
                'message': 'Failed to connect to database'
            })
        
        # Process each table
        for i, table_name in enumerate(selected_tables):
            # Update progress
            maintenance_status['current'] = i + 1
            maintenance_status['percentage'] = int(((i + 1) / len(selected_tables)) * 100)
            maintenance_status['message'] = f'Checking: {table_name}'
            
            print(f"\n[LOG] ====== Processing Table: {table_name} ======")
            
            # 1. CHECK TABLE
            print(f"[LOG] Step 1: Checking table structure...")
            check_result = check_table(connection, table_name)
            
            table_status = "OK"
            action_taken = "None"
            final_result = "Healthy"
            
            # Check if table has issues
            has_error = False
            for check_row in check_result:
                msg_type = check_row.get('Msg_type', '').lower()
                msg_text = check_row.get('Msg_text', '')
                
                if msg_type in ['error', 'warning'] or 'corrupt' in msg_text.lower():
                    has_error = True
                    table_status = "ERROR"
                    print(f"[LOG] ✗ Issue found: {msg_text}")
                    break
            
            if has_error:
                # 2. REPAIR TABLE if needed
                print(f"[LOG] Step 2: Repairing table...")
                repair_result = repair_table(connection, table_name)
                action_taken = "REPAIR"
                
                repair_success = False
                for repair_row in repair_result:
                    msg_type = repair_row.get('Msg_type', '').lower()
                    msg_text = repair_row.get('Msg_text', '')
                    
                    if msg_type == 'status' and 'ok' in msg_text.lower():
                        repair_success = True
                        print(f"[LOG] ✓ Repair successful")
                        break
                
                if repair_success:
                    # 3. OPTIMIZE TABLE after repair
                    print(f"[LOG] Step 3: Optimizing table...")
                    optimize_result = optimize_table(connection, table_name)
                    action_taken = "REPAIR + OPTIMIZE"
                    final_result = "Repaired & Optimized"
                    print(f"[LOG] ✓ Optimization complete")
                else:
                    final_result = "Repair Failed"
                    print(f"[LOG] ✗ Repair failed")
            else:
                # Table is OK, just optimize
                print(f"[LOG] ✓ Table is healthy")
                print(f"[LOG] Step 2: Optimizing table...")
                optimize_result = optimize_table(connection, table_name)
                action_taken = "OPTIMIZE"
                final_result = "Optimized"
                print(f"[LOG] ✓ Optimization complete")
            
            # Store result
            result_entry = {
                'table': table_name,
                'status': table_status,
                'action': action_taken,
                'result': final_result
            }
            check_results.append(result_entry)
            maintenance_status['results'].append(result_entry)
            
            print(f"[LOG] ====== Completed: {table_name} ======\n")
        
        connection.close()
        
        # Save log
        save_maintenance_log(check_results, database)
        
        maintenance_status['completed'] = True
        maintenance_status['is_running'] = False
        maintenance_status['message'] = f'Maintenance completed! {len(check_results)} tables processed.'
        
        return jsonify({
            'success': True,
            'message': f'Maintenance completed successfully!\n{len(check_results)} tables processed.',
            'results': check_results
        })
        
    except Exception as e:
        maintenance_status['error'] = str(e)
        maintenance_status['is_running'] = False
        return jsonify({
            'success': False,
            'message': f'Maintenance failed: {str(e)}'
        })


@app.route('/maintenance-status')
def get_maintenance_status():
    """Get current maintenance status"""
    return jsonify(maintenance_status)


@app.route('/open-data-folder', methods=['POST'])
def open_data_folder():
    """Open data folder in file explorer"""
    try:
        data_folder = os.path.abspath("data")
        if os.path.exists(data_folder):
            if os.name == 'nt':
                os.startfile(data_folder)
            elif sys.platform == 'darwin':
                subprocess.run(['open', data_folder])
            else:
                subprocess.run(['xdg-open', data_folder])
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'Data folder not found'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/check-saldo', methods=['POST'])
def check_saldo():
    """Check barang saldo data for specific month (format: th_barang_saldo_yyyyMM)"""
    try:
        data = request.get_json()
        host = data.get('host', '').strip()
        user = data.get('user', '').strip()
        password = data.get('password', '').strip()
        database = data.get('database', '').strip()
        check_date = data.get('checkDate', '').strip()  # Format: YYYY-MM
        
        if not all([host, user, database, check_date]):
            return jsonify({
                'success': False,
                'message': 'Please fill in all required fields!'
            })
        
        # Validate that check_date is last month only
        try:
            today = datetime.now()
            
            # Calculate last month
            if today.month == 1:
                last_month_year = today.year - 1
                last_month_month = 12
            else:
                last_month_year = today.year
                last_month_month = today.month - 1
            
            last_month_str = f"{last_month_year}-{last_month_month:02d}"
            
            if check_date != last_month_str:
                return jsonify({
                    'success': False,
                    'message': f'Only last month ({last_month_str}) can be processed. Selected: {check_date}'
                })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Date validation error: {str(e)}'
            })
        
        # Parse date to get yyyyMM format
        try:
            year, month = check_date.split('-')
            table_suffix = f"{year}{month}"  # e.g., "202601" from "2026-01"
            monthly_table = f"th_barang_saldo_{table_suffix}"
        except:
            return jsonify({
                'success': False,
                'message': 'Invalid date format. Use YYYY-MM format.'
            })
        
        connection = connect_to_mysql(host, user, password, database)
        
        if not connection:
            return jsonify({
                'success': False,
                'message': 'Connection failed. Please check your credentials.'
            })
        
        cursor = connection.cursor()
        
        # Check if monthly table exists
        cursor.execute(f"SHOW TABLES LIKE '{monthly_table}'")
        table_exists = cursor.fetchone() is not None
        
        if not table_exists:
            cursor.close()
            connection.close()
            return jsonify({
                'success': False,
                'needsFixing': False,
                'message': f'Table {monthly_table} does not exist in database.'
            })
        
        # Check if monthly table has data
        cursor.execute(f"SELECT COUNT(*) as count FROM `{monthly_table}`")
        monthly_count = cursor.fetchone()['count']
        
        if monthly_count > 0:
            cursor.close()
            connection.close()
            return jsonify({
                'success': True,
                'needsFixing': False,
                'message': f'✓ Table {monthly_table} exists and has {monthly_count:,} records. Data is OK!',
                'monthlyTable': monthly_table,
                'monthlyCount': monthly_count
            })
        
        # Monthly table is empty, check main table
        cursor.execute(f"""
            SELECT COUNT(*) as count 
            FROM th_barang_saldo 
            WHERE LEFT(tanggal, 7) = '{check_date}'
        """)
        main_count = cursor.fetchone()['count']
        
        cursor.close()
        connection.close()
        
        if main_count > 0:
            return jsonify({
                'success': True,
                'needsFixing': True,
                'message': f'⚠ Table {monthly_table} is EMPTY, but found {main_count:,} records in th_barang_saldo for period {check_date}. Ready to fix!',
                'monthlyTable': monthly_table,
                'monthlyCount': 0,
                'mainCount': main_count,
                'checkDate': check_date
            })
        else:
            return jsonify({
                'success': True,
                'needsFixing': False,
                'message': f'ℹ Table {monthly_table} is empty and no data found in th_barang_saldo for period {check_date}.',
                'monthlyTable': monthly_table,
                'monthlyCount': 0,
                'mainCount': 0
            })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })


@app.route('/fix-saldo', methods=['POST'])
def fix_saldo():
    """Fix barang saldo by moving data from main table to monthly table (th_barang_saldo_yyyyMM)"""
    try:
        data = request.get_json()
        host = data.get('host', '').strip()
        user = data.get('user', '').strip()
        password = data.get('password', '').strip()
        database = data.get('database', '').strip()
        check_date = data.get('checkDate', '').strip()  # Format: YYYY-MM
        monthly_table = data.get('monthlyTable', '').strip()
        
        if not all([host, user, database, check_date, monthly_table]):
            return jsonify({
                'success': False,
                'message': 'Missing required parameters!'
            })
        
        # Validate that check_date is last month only
        try:
            today = datetime.now()
            
            # Calculate last month
            if today.month == 1:
                last_month_year = today.year - 1
                last_month_month = 12
            else:
                last_month_year = today.year
                last_month_month = today.month - 1
            
            last_month_str = f"{last_month_year}-{last_month_month:02d}"
            
            if check_date != last_month_str:
                return jsonify({
                    'success': False,
                    'message': f'Security: Only last month ({last_month_str}) can be processed. Request denied.'
                })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Date validation error: {str(e)}'
            })
        
        connection = connect_to_mysql(host, user, password, database)
        
        if not connection:
            return jsonify({
                'success': False,
                'message': 'Connection failed. Please check your credentials.'
            })
        
        cursor = connection.cursor()
        
        try:
            # Start transaction
            connection.begin()
            
            # Step 1: Copy data from th_barang_saldo to monthly table
            insert_query = f"""
                INSERT INTO `{monthly_table}` 
                SELECT * FROM th_barang_saldo 
                WHERE LEFT(tanggal, 7) = '{check_date}'
            """
            cursor.execute(insert_query)
            inserted_count = cursor.rowcount
            
            # Step 2: Delete data from th_barang_saldo
            delete_query = f"""
                DELETE FROM th_barang_saldo 
                WHERE LEFT(tanggal, 7) = '{check_date}'
            """
            cursor.execute(delete_query)
            deleted_count = cursor.rowcount
            
            # Commit transaction
            connection.commit()
            
            cursor.close()
            connection.close()
            
            return jsonify({
                'success': True,
                'message': f'✓ Successfully moved {inserted_count:,} records from th_barang_saldo to {monthly_table}. {deleted_count:,} records deleted from main table.',
                'insertedCount': inserted_count,
                'deletedCount': deleted_count,
                'monthlyTable': monthly_table
            })
            
        except Exception as e:
            # Rollback on error
            connection.rollback()
            cursor.close()
            connection.close()
            
            return jsonify({
                'success': False,
                'message': f'Transaction failed and rolled back: {str(e)}'
            })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })


@app.route('/smart-audit-stream', methods=['POST'])
def smart_audit_stream():
    """Smart Audit Toko - Cross check with real-time progress streaming"""
    def generate():
        try:
            # Get request data from the request context
            from flask import Request
            req_data = request.get_data()
            data = json.loads(req_data)
            host = data.get('host', '').strip()
            user = data.get('user', '').strip()
            password = data.get('password', '').strip()
            database = data.get('database', '').strip()
            
            if not all([host, user, database]):
                yield f"data: {json.dumps({'error': True, 'message': 'Please fill in all required fields!'})}\n\n"
                return
            
            connection = connect_to_mysql(host, user, password, database)
            
            if not connection:
                yield f"data: {json.dumps({'error': True, 'message': 'Connection failed. Please check your credentials.'})}\n\n"
                return
        
            cursor = connection.cursor()
            
            # Step 1: Get all tm_barang with TOKO location and stock > 0
            print("[AUDIT] Getting tm_barang data...")
            yield f"data: {json.dumps({'type': 'progress', 'step': 'query', 'message': 'Querying tm_barang...'})}\n\n"
            
            cursor.execute("""
                SELECT kode_barang, kode_lokasi_toko, stock_on_hand*1 as stock
                FROM tm_barang 
                WHERE kode_lokasi_gudang = 'TOKO' 
                AND stock_on_hand*1 > 0
                ORDER BY kode_barang
            """)
            tm_barang_list = cursor.fetchall()
            total_tm_barang = len(tm_barang_list)
            
            print(f"[AUDIT] Found {total_tm_barang} items in tm_barang")
            yield f"data: {json.dumps({'type': 'progress', 'step': 'start', 'total': total_tm_barang, 'message': f'Found {total_tm_barang} items'})}\n\n"
        
            issues = []
            not_found_count = 0
            duplicate_count = 0
            match_tm_to_tt = 0
            
            # Step 2: For each tm_barang, check in tt_barang_saldo
            for idx, tm_item in enumerate(tm_barang_list):
                kode_barang = tm_item['kode_barang']
                kode_lokasi = tm_item['kode_lokasi_toko']
                stock_tm = tm_item['stock']
                
                # Send progress update every item
                current = idx + 1
                percent = int((current / total_tm_barang) * 100)
                yield f"data: {json.dumps({'type': 'progress', 'step': 'processing', 'current': current, 'total': total_tm_barang, 'percent': percent, 'kode_barang': kode_barang})}\n\n"
                
                # Check in tt_barang_saldo
                cursor.execute("""
                SELECT kode_barang, kode_lokasi_toko, stock_akhir*1 as stock
                FROM tt_barang_saldo
                WHERE kode_barang = %s 
                AND kode_lokasi_toko = %s
                AND stock_akhir*1 > 0
                """, (kode_barang, kode_lokasi))
                
                tt_items = cursor.fetchall()
                tt_count = len(tt_items)
                
                if tt_count == 0:
                    # Not found in tt_barang_saldo
                    not_found_count += 1
                    issues.append({
                        'kode_barang': kode_barang,
                        'kode_lokasi': kode_lokasi,
                        'count_tt': 0,
                        'issue': 'NOT_FOUND',
                        'issue_text': 'Not found in tt_barang_saldo'
                    })
                elif tt_count == 1:
                    # Perfect match (1-to-1)
                    match_tm_to_tt += 1
                elif tt_count > 1:
                    # Duplicate found in tt_barang_saldo
                    duplicate_count += 1
                    # Get kode_lokasi_toko from first duplicate record
                    kode_lokasi_toko = tt_items[0]['kode_lokasi_toko'] if tt_items else kode_lokasi
                    issues.append({
                        'kode_barang': kode_barang,
                        'kode_lokasi': kode_lokasi_toko,
                        'count_tt': tt_count,
                        'issue': 'DUPLICATE',
                        'issue_text': f'Duplicate! Found {tt_count} records (should be 1)'
                    })
            
            cursor.close()
            connection.close()
            
            # Send final result
            yield f"data: {json.dumps({'type': 'complete', 'success': True, 'summary': {'total_tm_barang': total_tm_barang, 'match_tm_to_tt': match_tm_to_tt, 'not_found': not_found_count, 'duplicate': duplicate_count, 'total_issues': len(issues)}, 'issues': issues})}\n\n"
            
        except Exception as e:
            print(f"[AUDIT ERROR] {str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'message': f'Audit error: {str(e)}'})}\n\n"
    
    return Response(stream_with_context(generate()), mimetype='text/event-stream')


def open_browser():
    """Open browser automatically"""
    webbrowser.open_new('http://localhost:5000')


def main():
    """Main entry point"""
    print("=" * 80)
    print("NAGACAGEUR - DATABASE MAINTENANCE & DATA MANAGEMENT TOOL")
    print("=" * 80)
    print("Starting Flask server on http://localhost:5000")
    print("Browser will open automatically in 2 seconds...")
    print("=" * 80)
    
    # Auto-open browser after 2 seconds
    Timer(2, open_browser).start()
    
    # Run Flask app
    app.run(host='localhost', port=5000, debug=False, use_reloader=False)


if __name__ == '__main__':
    main()
