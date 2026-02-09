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
        
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        log_file = os.path.join(data_folder, f"maintenance_log_{timestamp}.txt")
        
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


def save_saldo_checker_log(operation, database_name, check_date, monthly_table, result_data):
    """Save TH Barang Saldo Checker log file"""
    try:
        data_folder = "data"
        if not os.path.exists(data_folder):
            os.makedirs(data_folder)
        
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        log_file = os.path.join(data_folder, f"saldo_checker_log_{timestamp}.txt")
        
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("=" * 100 + "\n")
            f.write("TH BARANG SALDO CHECKER LOG\n")
            f.write("=" * 100 + "\n")
            f.write(f"Date/Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Database: {database_name}\n")
            f.write(f"Operation: {operation}\n")
            f.write(f"Check Period: {check_date}\n")
            f.write(f"Monthly Table: {monthly_table}\n")
            f.write("=" * 100 + "\n\n")
            
            if operation == "CHECK":
                f.write(f"Monthly Count: {result_data.get('monthlyCount', 0):,}\n")
                f.write(f"Main Table Count: {result_data.get('mainCount', 0):,}\n")
                f.write(f"Needs Fixing: {result_data.get('needsFixing', False)}\n")
                f.write(f"Needs Creating: {result_data.get('needsCreating', False)}\n")
            elif operation == "CREATE_TABLE":
                f.write(f"Result: Table created successfully\n")
            elif operation == "FIX_SALDO":
                f.write(f"Inserted Count: {result_data.get('insertedCount', 0):,}\n")
                f.write(f"Deleted Count: {result_data.get('deletedCount', 0):,}\n")
                f.write(f"Result: Data moved successfully\n")
            
            f.write("\n" + "=" * 100 + "\n\n")
        
        print(f"\n[LOG] Saldo checker log saved to: {log_file}")
        
    except Exception as e:
        print(f"[LOG] Error saving saldo checker log: {str(e)}")


def save_audit_log(database_name, summary_data, total_issues, issues_phase1, issues_phase2):
    """Save Smart Audit Toko log file"""
    try:
        data_folder = "data"
        if not os.path.exists(data_folder):
            os.makedirs(data_folder)
        
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        log_file = os.path.join(data_folder, f"smart_audit_log_{timestamp}.txt")
        
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("=" * 100 + "\n")
            f.write("SMART AUDIT TOKO LOG\n")
            f.write("=" * 100 + "\n")
            f.write(f"Date/Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Database: {database_name}\n")
            f.write("=" * 100 + "\n\n")
            
            f.write("PHASE 1: tm_barang → tt_barang_saldo\n")
            f.write("-" * 100 + "\n")
            phase1 = summary_data.get('phase1', {})
            f.write(f"Total tm_barang: {phase1.get('total_tm_barang', 0):,}\n")
            f.write(f"Match (TM→TT): {phase1.get('match_tm_to_tt', 0):,}\n")
            f.write(f"Not Found: {phase1.get('not_found', 0):,}\n")
            f.write(f"Duplicate: {phase1.get('duplicate', 0):,}\n")
            f.write(f"Phase 1 Issues: {phase1.get('issues', 0):,}\n")
            f.write("\n")
            
            # Detail Phase 1 Issues
            if issues_phase1:
                f.write("PHASE 1 - DETAIL TEMUAN:\n")
                f.write("-" * 100 + "\n")
                f.write(f"{'No':<5} {'Kode Barang':<20} {'Kode Lokasi':<15} {'Issue Type':<25} {'Description':<35}\n")
                f.write("-" * 100 + "\n")
                for idx, issue in enumerate(issues_phase1, 1):
                    f.write(f"{idx:<5} {issue.get('kode_barang', ''):<20} {issue.get('kode_lokasi', ''):<15} {issue.get('issue', ''):<25} {issue.get('issue_text', ''):<35}\n")
                f.write("-" * 100 + "\n\n")
            else:
                f.write("PHASE 1 - No issues found\n\n")
            
            f.write("PHASE 2: tt_barang_saldo → tm_barang\n")
            f.write("-" * 100 + "\n")
            phase2 = summary_data.get('phase2', {})
            f.write(f"Total tt_barang: {phase2.get('total_tt_barang', 0):,}\n")
            f.write(f"Match (TT→TM): {phase2.get('match_tt_to_tm', 0):,}\n")
            f.write(f"Not Found: {phase2.get('not_found', 0):,}\n")
            f.write(f"Duplicate: {phase2.get('duplicate', 0):,}\n")
            f.write(f"Phase 2 Issues: {phase2.get('issues', 0):,}\n")
            f.write("\n")
            
            # Detail Phase 2 Issues
            if issues_phase2:
                f.write("PHASE 2 - DETAIL TEMUAN:\n")
                f.write("-" * 100 + "\n")
                f.write(f"{'No':<5} {'Kode Barang':<20} {'Kode Lokasi':<15} {'Issue Type':<25} {'Description':<35}\n")
                f.write("-" * 100 + "\n")
                for idx, issue in enumerate(issues_phase2, 1):
                    f.write(f"{idx:<5} {issue.get('kode_barang', ''):<20} {issue.get('kode_lokasi', ''):<15} {issue.get('issue', ''):<25} {issue.get('issue_text', ''):<35}\n")
                f.write("-" * 100 + "\n\n")
            else:
                f.write("PHASE 2 - No issues found\n\n")
            
            f.write("SUMMARY\n")
            f.write("-" * 100 + "\n")
            f.write(f"Total Issues Found: {total_issues:,}\n")
            f.write(f"Audit Status: {'PASSED' if total_issues == 0 else 'FAILED'}\n")
            f.write("\n" + "=" * 100 + "\n\n")
        
        print(f"\n[LOG] Smart audit log saved to: {log_file}")
        
    except Exception as e:
        print(f"[LOG] Error saving smart audit log: {str(e)}")


def save_smart_audit_fixing_log(database_name, fixing_result):
    """Save Smart Audit Fixing log file"""
    try:
        data_folder = "data"
        if not os.path.exists(data_folder):
            os.makedirs(data_folder)
        
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        log_file = os.path.join(data_folder, f"smart_audit_fixing_{timestamp}.txt")
        
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("=" * 100 + "\n")
            f.write("SMART AUDIT TOKO - FIXING LOG\n")
            f.write("=" * 100 + "\n")
            f.write(f"Date/Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Database: {database_name}\n")
            f.write("=" * 100 + "\n\n")
            
            # Summary
            f.write("FIXING SUMMARY\n")
            f.write("-" * 100 + "\n")
            f.write(f"Duplicates Deleted: {fixing_result.get('duplicates_deleted', 0):,}\n")
            f.write(f"Missing Records Inserted: {fixing_result.get('missing_inserted', 0):,}\n")
            f.write(f"Total Fixed: {fixing_result.get('total_fixed', 0):,}\n")
            f.write("\n")
            
            # Detail Duplicates Deleted
            duplicates_detail = fixing_result.get('duplicates_detail', [])
            if duplicates_detail:
                f.write("DETAIL DUPLIKAT YANG DIHAPUS:\n")
                f.write("-" * 100 + "\n")
                f.write(f"{'No':<5} {'Kode Barang':<20} {'Kode Lokasi':<15} {'Deleted Count':<15}\n")
                f.write("-" * 100 + "\n")
                for idx, item in enumerate(duplicates_detail, 1):
                    f.write(f"{idx:<5} {item.get('kode_barang', ''):<20} {item.get('kode_lokasi', ''):<15} {item.get('deleted_count', 0):<15}\n")
                f.write("-" * 100 + "\n\n")
            
            # Detail Missing Inserted
            missing_detail = fixing_result.get('missing_detail', [])
            if missing_detail:
                f.write("DETAIL DATA YANG DIINSERT:\n")
                f.write("-" * 100 + "\n")
                f.write(f"{'No':<5} {'Kode Barang':<20} {'Kode Lokasi':<15} {'Stock':<10}\n")
                f.write("-" * 100 + "\n")
                for idx, item in enumerate(missing_detail, 1):
                    f.write(f"{idx:<5} {item.get('kode_barang', ''):<20} {item.get('kode_lokasi', ''):<15} {item.get('stock', 0):<10}\n")
                f.write("-" * 100 + "\n\n")
            
            f.write("=" * 100 + "\n\n")
        
        print(f"\n[LOG] Smart audit fixing log saved to: {log_file}")
        
    except Exception as e:
        print(f"[LOG] Error saving smart audit fixing log: {str(e)}")



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
                'success': True,
                'needsFixing': False,
                'needsCreating': True,
                'message': f'⚠ Table {monthly_table} does not exist in database. You can create it now.',
                'monthlyTable': monthly_table,
                'checkDate': check_date
            })
        
        # Check if monthly table has data
        cursor.execute(f"SELECT COUNT(*) as count FROM `{monthly_table}`")
        monthly_count = cursor.fetchone()['count']
        
        if monthly_count > 0:
            cursor.close()
            connection.close()
            
            # Log the check result
            result_data = {'monthlyCount': monthly_count, 'mainCount': 0, 'needsFixing': False, 'needsCreating': False}
            save_saldo_checker_log("CHECK", database, check_date, monthly_table, result_data)
            
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
            # Log the check result
            result_data = {'monthlyCount': 0, 'mainCount': main_count, 'needsFixing': True, 'needsCreating': False}
            save_saldo_checker_log("CHECK", database, check_date, monthly_table, result_data)
            
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
            # Log the check result
            result_data = {'monthlyCount': 0, 'mainCount': 0, 'needsFixing': False, 'needsCreating': False}
            save_saldo_checker_log("CHECK", database, check_date, monthly_table, result_data)
            
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
            
            # Log the fix result
            result_data = {'insertedCount': inserted_count, 'deletedCount': deleted_count}
            save_saldo_checker_log("FIX_SALDO", database, check_date, monthly_table, result_data)
            
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


@app.route('/create-table-saldo', methods=['POST'])
def create_table_saldo():
    """Create monthly table th_barang_saldo_yyyyMM with structure from main table"""
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
            # Check if table already exists
            cursor.execute(f"SHOW TABLES LIKE '{monthly_table}'")
            if cursor.fetchone() is not None:
                cursor.close()
                connection.close()
                return jsonify({
                    'success': False,
                    'message': f'Table {monthly_table} already exists!'
                })
            
            # Create table with same structure as th_barang_saldo
            create_query = f"""
                CREATE TABLE `{monthly_table}` LIKE th_barang_saldo
            """
            cursor.execute(create_query)
            connection.commit()
            
            cursor.close()
            connection.close()
            
            # Log the create table result
            result_data = {}
            save_saldo_checker_log("CREATE_TABLE", database, check_date, monthly_table, result_data)
            
            return jsonify({
                'success': True,
                'message': f'✓ Successfully created table {monthly_table}!',
                'monthlyTable': monthly_table
            })
            
        except Exception as e:
            # Rollback on error
            connection.rollback()
            cursor.close()
            connection.close()
            
            return jsonify({
                'success': False,
                'message': f'Failed to create table: {str(e)}'
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
            
            # ============================================================
            # PHASE 1: Check tm_barang -> tt_barang_saldo
            # ============================================================
            print("[AUDIT PHASE 1] Getting tm_barang data...")
            yield f"data: {json.dumps({'type': 'progress', 'step': 'query', 'message': 'Phase 1: Querying tm_barang...'})}\n\n"
            
            cursor.execute("""
                SELECT kode_barang, kode_lokasi_toko, stock_on_hand*1 as stock
                FROM tm_barang 
                WHERE kode_lokasi_gudang = 'TOKO' 
                AND stock_on_hand*1 > 0
                ORDER BY kode_barang
            """)
            tm_barang_list = cursor.fetchall()
            total_tm_barang = len(tm_barang_list)
            
            print(f"[AUDIT PHASE 1] Found {total_tm_barang} items in tm_barang")
            yield f"data: {json.dumps({'type': 'progress', 'step': 'start_phase1', 'total': total_tm_barang, 'message': f'Phase 1: Found {total_tm_barang} items in tm_barang'})}\n\n"
        
            issues_phase1 = []
            not_found_tm_to_tt = 0
            duplicate_tm_to_tt = 0
            match_tm_to_tt = 0
            
            # Check each tm_barang in tt_barang_saldo
            for idx, tm_item in enumerate(tm_barang_list):
                kode_barang = tm_item['kode_barang']
                kode_lokasi = tm_item['kode_lokasi_toko']
                stock_tm = tm_item['stock']
                
                # Send progress update
                current = idx + 1
                percent = int((current / total_tm_barang) * 50)  # 0-50% for phase 1
                yield f"data: {json.dumps({'type': 'progress', 'step': 'processing_phase1', 'current': current, 'total': total_tm_barang, 'percent': percent, 'kode_barang': kode_barang, 'message': f'Phase 1: Processing {current}/{total_tm_barang}'})}\n\n"
                
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
                    not_found_tm_to_tt += 1
                    issues_phase1.append({
                        'kode_barang': kode_barang,
                        'kode_lokasi': kode_lokasi,
                        'count_tt': 0,
                        'issue': 'TM_NOT_IN_TT',
                        'issue_text': '[TM→TT] Not found in tt_barang_saldo'
                    })
                elif tt_count == 1:
                    match_tm_to_tt += 1
                elif tt_count > 1:
                    duplicate_tm_to_tt += 1
                    kode_lokasi_toko = tt_items[0]['kode_lokasi_toko'] if tt_items else kode_lokasi
                    issues_phase1.append({
                        'kode_barang': kode_barang,
                        'kode_lokasi': kode_lokasi_toko,
                        'count_tt': tt_count,
                        'issue': 'TM_DUPLICATE_IN_TT',
                        'issue_text': f'[TM→TT] Duplicate in tt! Found {tt_count} records'
                    })
            
            print(f"[AUDIT PHASE 1] Completed. Match: {match_tm_to_tt}, Not Found: {not_found_tm_to_tt}, Duplicate: {duplicate_tm_to_tt}")
            
            # ============================================================
            # PHASE 2: Check tt_barang_saldo -> tm_barang
            # ============================================================
            print("[AUDIT PHASE 2] Getting tt_barang_saldo data...")
            yield f"data: {json.dumps({'type': 'progress', 'step': 'query_phase2', 'message': 'Phase 2: Querying tt_barang_saldo...'})}\n\n"
            
            cursor.execute("""
                SELECT kode_barang, kode_lokasi_toko, stock_akhir*1 as stock
                FROM tt_barang_saldo
                WHERE kode_lokasi_gudang = 'TOKO' 
                AND stock_akhir*1 > 0
                ORDER BY kode_barang
            """)
            tt_barang_list = cursor.fetchall()
            total_tt_barang = len(tt_barang_list)
            
            print(f"[AUDIT PHASE 2] Found {total_tt_barang} items in tt_barang_saldo")
            yield f"data: {json.dumps({'type': 'progress', 'step': 'start_phase2', 'total': total_tt_barang, 'message': f'Phase 2: Found {total_tt_barang} items in tt_barang_saldo'})}\n\n"
        
            issues_phase2 = []
            not_found_tt_to_tm = 0
            duplicate_tt_to_tm = 0
            match_tt_to_tm = 0
            
            # Check each tt_barang_saldo in tm_barang
            for idx, tt_item in enumerate(tt_barang_list):
                kode_barang = tt_item['kode_barang']
                kode_lokasi = tt_item['kode_lokasi_toko']
                stock_tt = tt_item['stock']
                
                # Send progress update
                current = idx + 1
                percent = 50 + int((current / total_tt_barang) * 50)  # 50-100% for phase 2
                yield f"data: {json.dumps({'type': 'progress', 'step': 'processing_phase2', 'current': current, 'total': total_tt_barang, 'percent': percent, 'kode_barang': kode_barang, 'message': f'Phase 2: Processing {current}/{total_tt_barang}'})}\n\n"
                
                # Check in tm_barang
                cursor.execute("""
                SELECT kode_barang, kode_lokasi_toko, stock_on_hand*1 as stock
                FROM tm_barang
                WHERE kode_barang = %s 
                AND kode_lokasi_toko = %s
                AND kode_lokasi_gudang = 'TOKO'
                AND stock_on_hand*1 > 0
                """, (kode_barang, kode_lokasi))
                
                tm_items = cursor.fetchall()
                tm_count = len(tm_items)
                
                if tm_count == 0:
                    not_found_tt_to_tm += 1
                    issues_phase2.append({
                        'kode_barang': kode_barang,
                        'kode_lokasi': kode_lokasi,
                        'count_tm': 0,
                        'issue': 'TT_NOT_IN_TM',
                        'issue_text': '[TT→TM] Not found in tm_barang'
                    })
                elif tm_count == 1:
                    match_tt_to_tm += 1
                elif tm_count > 1:
                    duplicate_tt_to_tm += 1
                    kode_lokasi_toko = tm_items[0]['kode_lokasi_toko'] if tm_items else kode_lokasi
                    issues_phase2.append({
                        'kode_barang': kode_barang,
                        'kode_lokasi': kode_lokasi_toko,
                        'count_tm': tm_count,
                        'issue': 'TT_DUPLICATE_IN_TM',
                        'issue_text': f'[TT→TM] Duplicate in tm! Found {tm_count} records'
                    })
            
            print(f"[AUDIT PHASE 2] Completed. Match: {match_tt_to_tm}, Not Found: {not_found_tt_to_tm}, Duplicate: {duplicate_tt_to_tm}")
            
            # Combine all issues
            all_issues = issues_phase1 + issues_phase2
            
            cursor.close()
            connection.close()
            
            # Prepare summary data for logging
            summary_data = {
                'phase1': {
                    'total_tm_barang': total_tm_barang,
                    'match_tm_to_tt': match_tm_to_tt,
                    'not_found': not_found_tm_to_tt,
                    'duplicate': duplicate_tm_to_tt,
                    'issues': len(issues_phase1)
                },
                'phase2': {
                    'total_tt_barang': total_tt_barang,
                    'match_tt_to_tm': match_tt_to_tm,
                    'not_found': not_found_tt_to_tm,
                    'duplicate': duplicate_tt_to_tm,
                    'issues': len(issues_phase2)
                }
            }
            
            # Save audit log
            save_audit_log(database, summary_data, len(all_issues), issues_phase1, issues_phase2)
            
            # Send final result with both phases
            yield f"data: {json.dumps({'type': 'complete', 'success': True, 'summary': summary_data | {'total_issues': len(all_issues)}, 'issues': all_issues})}\n\n"
            
        except Exception as e:
            print(f"[AUDIT ERROR] {str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'message': f'Audit error: {str(e)}'})}\n\n"
    
    return Response(stream_with_context(generate()), mimetype='text/event-stream')


@app.route('/fix-smart-audit-stream', methods=['POST'])
def fix_smart_audit_stream():
    """Fix Smart Audit Issues - Delete duplicates and insert missing data with real-time progress"""
    def generate():
        try:
            # Get request data
            from flask import Request
            req_data = request.get_data()
            data = json.loads(req_data)
            host = data.get('host', '').strip()
            user = data.get('user', '').strip()
            password = data.get('password', '').strip()
            database = data.get('database', '').strip()
            issues = data.get('issues', [])
            
            if not all([host, user, database]):
                yield f"data: {json.dumps({'error': True, 'message': 'Please fill in all required fields!'})}\n\n"
                return
            
            if not issues:
                yield f"data: {json.dumps({'error': True, 'message': 'No issues to fix!'})}\n\n"
                return
            
            connection = connect_to_mysql(host, user, password, database)
            
            if not connection:
                yield f"data: {json.dumps({'error': True, 'message': 'Connection failed. Please check your credentials.'})}\n\n"
                return
            
            cursor = connection.cursor()
            
            # Filter issues that need fixing
            duplicate_issues = [issue for issue in issues if issue.get('issue') == 'TM_DUPLICATE_IN_TT']
            missing_issues = [issue for issue in issues if issue.get('issue') == 'TM_NOT_IN_TT']
            
            total_fixes = len(duplicate_issues) + len(missing_issues)
            
            print(f"[FIXING] Total fixes needed: {total_fixes} (Duplicates: {len(duplicate_issues)}, Missing: {len(missing_issues)})")
            yield f"data: {json.dumps({'type': 'progress', 'step': 'start', 'total': total_fixes, 'message': f'Starting fix process... {total_fixes} issues to fix'})}\n\n"
            
            duplicates_deleted = 0
            missing_inserted = 0
            duplicates_detail = []
            missing_detail = []
            current_progress = 0
            
            # ============================================================
            # STEP 1: Fix Duplicates - Delete extras, keep only 1
            # ============================================================
            print("[FIXING] Step 1: Fixing duplicates...")
            yield f"data: {json.dumps({'type': 'progress', 'step': 'fixing_duplicates', 'message': 'Step 1: Fixing duplicates...'})}\n\n"
            
            for idx, issue in enumerate(duplicate_issues):
                kode_barang = issue.get('kode_barang')
                kode_lokasi = issue.get('kode_lokasi')
                
                current_progress += 1
                percent = int((current_progress / total_fixes) * 100)
                yield f"data: {json.dumps({'type': 'progress', 'step': 'processing', 'current': current_progress, 'total': total_fixes, 'percent': percent, 'message': f'Fixing duplicate: {kode_barang} @ {kode_lokasi}'})}\n\n"
                
                try:
                    # Get count of duplicate records
                    cursor.execute("""
                        SELECT COUNT(*) as count FROM tt_barang_saldo
                        WHERE kode_barang = %s 
                        AND kode_lokasi_toko = %s
                        AND stock_akhir*1 > 0
                    """, (kode_barang, kode_lokasi))
                    
                    count_result = cursor.fetchone()
                    duplicate_count = count_result['count'] if count_result else 0
                    
                    if duplicate_count > 1:
                        # Delete duplicates, keep only 1
                        # Delete using WHERE clause with LIMIT (delete all except first)
                        deleted_count = 0
                        for i in range(duplicate_count - 1):
                            cursor.execute("""
                                DELETE FROM tt_barang_saldo 
                                WHERE kode_barang = %s 
                                AND kode_lokasi_toko = %s
                                AND stock_akhir*1 > 0
                                LIMIT 1
                            """, (kode_barang, kode_lokasi))
                            deleted_count += cursor.rowcount
                        
                        connection.commit()
                        
                        duplicates_deleted += deleted_count
                        duplicates_detail.append({
                            'kode_barang': kode_barang,
                            'kode_lokasi': kode_lokasi,
                            'deleted_count': deleted_count
                        })
                        
                        print(f"[FIXING] Deleted {deleted_count} duplicate(s) for {kode_barang} @ {kode_lokasi}")
                        
                except Exception as e:
                    print(f"[FIXING ERROR] Failed to fix duplicate {kode_barang}: {str(e)}")
                    yield f"data: {json.dumps({'type': 'warning', 'message': f'Failed to fix duplicate {kode_barang}: {str(e)}'})}\n\n"
            
            # ============================================================
            # STEP 2: Fix Missing - Insert from tm_barang to tt_barang_saldo
            # ============================================================
            print("[FIXING] Step 2: Inserting missing records...")
            yield f"data: {json.dumps({'type': 'progress', 'step': 'inserting_missing', 'message': 'Step 2: Inserting missing records...'})}\n\n"
            
            for idx, issue in enumerate(missing_issues):
                kode_barang = issue.get('kode_barang')
                kode_lokasi = issue.get('kode_lokasi')
                
                current_progress += 1
                percent = int((current_progress / total_fixes) * 100)
                yield f"data: {json.dumps({'type': 'progress', 'step': 'processing', 'current': current_progress, 'total': total_fixes, 'percent': percent, 'message': f'Inserting missing: {kode_barang} @ {kode_lokasi}'})}\n\n"
                
                try:
                    # Get data from tm_barang
                    cursor.execute("""
                        SELECT * FROM tm_barang
                        WHERE kode_barang = %s 
                        AND kode_lokasi_toko = %s
                        AND kode_lokasi_gudang = 'TOKO'
                        AND stock_on_hand*1 > 0
                        LIMIT 1
                    """, (kode_barang, kode_lokasi))
                    
                    tm_data = cursor.fetchone()
                    
                    if tm_data:
                        # Prepare data for insert to tt_barang_saldo - ALL STRING FORMAT
                        kode_barang_val = str(tm_data.get('kode_barang', ''))
                        kode_lokasi_toko_val = str(tm_data.get('kode_lokasi_toko', ''))
                        kode_lokasi_gudang_val = str(tm_data.get('kode_lokasi_gudang', ''))
                        kode_dept_val = str(tm_data.get('kode_dept', ''))
                        
                        stock = tm_data.get('stock_on_hand', 0) * 1
                        stock_str = str(stock)
                        
                        berat = tm_data.get('berat', 0) * 1 if tm_data.get('berat') else 0
                        berat_str = str(berat)
                        
                        berat_asli = tm_data.get('berat_asli', 0) * 1 if tm_data.get('berat_asli') else 0
                        berat_asli_str = str(berat_asli)
                        
                        # Get today date in yyyy-MM-dd format
                        today_date = datetime.now().strftime('%Y-%m-%d')
                        
                        print(f"[FIXING] Preparing INSERT for {kode_barang_val} @ {kode_lokasi_toko_val}")
                        print(f"[FIXING] Values: kode_dept={kode_dept_val}, stock={stock_str}, berat={berat_str}, berat_asli={berat_asli_str}, date={today_date}")
                        
                        insert_query = """
                            INSERT INTO tt_barang_saldo 
                            (kode_barang, kode_lokasi_toko, kode_lokasi_gudang, kode_dept,
                             stock_awal, stock_in, stock_out, stock_akhir, 
                             berat_awal, berat_awal_asli, berat_akhir, berat_akhir_asli, tanggal)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
                        
                        cursor.execute(insert_query, (
                            kode_barang_val,
                            kode_lokasi_toko_val,
                            kode_lokasi_gudang_val,
                            kode_dept_val,   # kode_dept
                            stock_str,       # stock_awal
                            '0',             # stock_in
                            '0',             # stock_out
                            stock_str,       # stock_akhir
                            berat_str,       # berat_awal
                            berat_asli_str,  # berat_awal_asli
                            berat_str,       # berat_akhir
                            berat_asli_str,  # berat_akhir_asli
                            today_date       # tanggal
                        ))
                        
                        affected_rows = cursor.rowcount
                        connection.commit()
                        
                        print(f"[FIXING] INSERT affected {affected_rows} row(s) for {kode_barang_val} @ {kode_lokasi_toko_val}")
                        
                        missing_inserted += 1
                        missing_detail.append({
                            'kode_barang': kode_barang,
                            'kode_lokasi': kode_lokasi,
                            'stock': stock
                        })
                        
                        print(f"[FIXING] ✓ Successfully inserted missing record for {kode_barang_val} @ {kode_lokasi_toko_val}")
                    else:
                        print(f"[FIXING WARNING] Data not found in tm_barang for {kode_barang} @ {kode_lokasi}")
                        yield f"data: {json.dumps({'type': 'warning', 'message': f'Data not found in tm_barang: {kode_barang} @ {kode_lokasi}'})}\n\n"
                        
                except Exception as e:
                    print(f"[FIXING ERROR] Failed to insert {kode_barang}: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    yield f"data: {json.dumps({'type': 'warning', 'message': f'Failed to insert {kode_barang}: {str(e)}'})}\n\n"
            
            cursor.close()
            connection.close()
            
            # Prepare fixing result
            fixing_result = {
                'duplicates_deleted': duplicates_deleted,
                'missing_inserted': missing_inserted,
                'total_fixed': duplicates_deleted + missing_inserted,
                'duplicates_detail': duplicates_detail,
                'missing_detail': missing_detail
            }
            
            # Save fixing log
            save_smart_audit_fixing_log(database, fixing_result)
            
            # Send final result
            yield f"data: {json.dumps({'type': 'complete', 'success': True, 'result': fixing_result})}\n\n"
            
        except Exception as e:
            print(f"[FIXING ERROR] {str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'message': f'Fixing error: {str(e)}'})}\n\n"
    
    return Response(stream_with_context(generate()), mimetype='text/event-stream')


def open_browser():
    """Open browser automatically"""
    webbrowser.open_new('http://localhost:5000')


def main():
    """Main entry point"""
    print("=" * 80)
    print("NAGACHECK - DATABASE MAINTENANCE & DATA MANAGEMENT TOOL")
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
