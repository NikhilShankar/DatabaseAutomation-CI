from flask import Flask, render_template, request
import pymysql
import os

app = Flask(__name__)

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'db'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'rootpass'),
    'database': os.getenv('DB_NAME', 'nyc311')
}

def get_db_connection():
    """Create database connection"""
    return pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)

@app.route('/')
def index():
    """Main search page with filters and pagination"""
    # Get filter parameters
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    borough = request.args.get('borough', '')
    complaint_type = request.args.get('complaint_type', '')
    page = int(request.args.get('page', 1))
    per_page = 50

    conn = get_db_connection()
    cursor = conn.cursor()

    # Build WHERE clause dynamically
    where_clauses = []
    params = []

    if date_from:
        where_clauses.append("created_date >= %s")
        params.append(date_from)
    if date_to:
        where_clauses.append("created_date <= %s")
        params.append(date_to)
    if borough and borough != 'ALL':
        where_clauses.append("borough = %s")
        params.append(borough)
    if complaint_type:
        where_clauses.append("complaint_type LIKE %s")
        params.append(f"%{complaint_type}%")

    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

    # Get total count for pagination
    count_query = "SELECT COUNT(*) as total FROM service_requests WHERE " + where_sql
    cursor.execute(count_query, params)
    total_records = cursor.fetchone()['total']
    total_pages = (total_records + per_page - 1) // per_page

    # Get paginated results
    offset = (page - 1) * per_page
    data_query = """
        SELECT unique_key, created_date, closed_date, agency, complaint_type,
               descriptor, borough, latitude, longitude
        FROM service_requests
        WHERE """ + where_sql + """
        ORDER BY created_date DESC
        LIMIT %s OFFSET %s
    """
    cursor.execute(data_query, params + [per_page, offset])
    results = cursor.fetchall()

    # Get distinct boroughs for dropdown
    cursor.execute("SELECT DISTINCT borough FROM service_requests ORDER BY borough")
    boroughs = [row['borough'] for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    return render_template('index.html',
                           results=results,
                           boroughs=boroughs,
                           total_records=total_records,
                           page=page,
                           total_pages=total_pages,
                           date_from=date_from,
                           date_to=date_to,
                           borough=borough,
                           complaint_type=complaint_type)

@app.route('/aggregate')
def aggregate():
    """Aggregate view - complaints per borough"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get complaints per borough
    cursor.execute("""
        SELECT
            borough,
            COUNT(*) as total_complaints,
            COUNT(CASE WHEN closed_date IS NOT NULL THEN 1 END) as closed_complaints,
            COUNT(CASE WHEN closed_date IS NULL THEN 1 END) as open_complaints,
            MIN(created_date) as earliest_complaint,
            MAX(created_date) as latest_complaint
        FROM service_requests
        GROUP BY borough
        ORDER BY total_complaints DESC
    """)
    borough_stats = cursor.fetchall()

    # Get top complaint types
    cursor.execute("""
        SELECT
            complaint_type,
            COUNT(*) as count
        FROM service_requests
        WHERE complaint_type IS NOT NULL
        GROUP BY complaint_type
        ORDER BY count DESC
        LIMIT 10
    """)
    top_complaints = cursor.fetchall()

    # Get overall statistics
    cursor.execute("""
        SELECT
            COUNT(*) as total,
            COUNT(CASE WHEN closed_date IS NOT NULL THEN 1 END) as closed,
            COUNT(CASE WHEN closed_date IS NULL THEN 1 END) as open,
            COUNT(DISTINCT agency) as agencies,
            COUNT(DISTINCT complaint_type) as complaint_types
        FROM service_requests
    """)
    overall_stats = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template('aggregate.html',
                           borough_stats=borough_stats,
                           top_complaints=top_complaints,
                           overall_stats=overall_stats)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
