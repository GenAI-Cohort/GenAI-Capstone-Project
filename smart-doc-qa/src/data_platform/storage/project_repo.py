from config.db_connection import get_connection

def get_project_id_from_project(project_name: str):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT id FROM public.projects WHERE name = %s;", (project_name,))
            rows = cur.fetchall()
            for row in rows:
                print(row)
        except Exception as e:
            print(f"Database error: {e}")
        finally:
            if conn:
                cur.close()
                conn.close()
        return row[0]  # Assuming project name is unique and returns a single id    