import os
import sqlite3
import pandas as pd
import gc
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Academic Risk Monitoring System")

# Mount static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

class StudentDatabase:
    def __init__(self, db_path="estudiantes.db", csv_path="ulead_visualizacion_800k.csv"):
        self.db_path = db_path
        self.csv_path = csv_path
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        if os.path.exists(self.db_path):
            conn = self._get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT COUNT(*) FROM estudiantes")
                count = cursor.fetchone()[0]
                if count > 0:
                    print(f"Database already populated with {count} records.")
                    conn.close()
                    return
            except sqlite3.OperationalError:
                pass
            conn.close()

        print("Initializing database from CSV. Loading in chunks...")
        conn = self._get_connection()
        cursor = conn.cursor()
        
        chunk_size = 100000
        for chunk in pd.read_csv(self.csv_path, chunksize=chunk_size):
            chunk.to_sql("estudiantes", conn, if_exists="append", index=False)
            
        print("Creating database indexes...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_modalidad ON estudiantes(modalidad)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_carrera ON estudiantes(carrera)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_riesgo ON estudiantes(riesgo_academico)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trabaja ON estudiantes(trabaja)")
        conn.commit()
        conn.close()
        print("Database initialization completed.")

    def get_overall_stats(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT riesgo_academico, COUNT(*) as qty FROM estudiantes GROUP BY riesgo_academico")
        rows = cursor.fetchall()
        
        stats = {row['riesgo_academico']: row['qty'] for row in rows}
        total = sum(stats.values())
        percentages = {k: round((v / total) * 100, 2) for k, v in stats.items()}
        conn.close()
        return {'total_students': total, 'risk_distribution': percentages}

    def get_modality_stats(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT modalidad, riesgo_academico, COUNT(*) as count 
            FROM estudiantes 
            GROUP BY modalidad, riesgo_academico
        """)
        rows = cursor.fetchall()
        
        result = {}
        for row in rows:
            mod = row['modalidad']
            risk = row['riesgo_academico']
            count = row['count']
            if mod not in result:
                result[mod] = {'Bajo': 0, 'Medio': 0, 'Alto': 0, 'Total': 0}
            result[mod][risk] = count
            result[mod]['Total'] += count

        for mod, counts in result.items():
            tot = counts['Total']
            for r in ['Bajo', 'Medio', 'Alto']:
                counts[r] = round((counts[r] / tot) * 100, 2)
            del counts['Total']
            
        conn.close()
        return result

    def get_attendance_stats(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT modalidad, riesgo_academico, AVG(asistencia) as avg_asistencia 
            FROM estudiantes 
            GROUP BY modalidad, riesgo_academico
        """)
        rows = cursor.fetchall()
        
        result = {}
        for row in rows:
            mod = row['modalidad']
            risk = row['riesgo_academico']
            val = round(row['avg_asistencia'], 2)
            if mod not in result:
                result[mod] = {}
            result[mod][risk] = val
            
        conn.close()
        return result

    def get_career_stats(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT carrera, riesgo_academico, COUNT(*) as count 
            FROM estudiantes 
            GROUP BY carrera, riesgo_academico
        """)
        rows = cursor.fetchall()
        
        result = {}
        for row in rows:
            carrera = row['carrera']
            risk = row['riesgo_academico']
            count = row['count']
            if carrera not in result:
                result[carrera] = {'Bajo': 0, 'Medio': 0, 'Alto': 0, 'Total': 0}
            result[carrera][risk] = count
            result[carrera]['Total'] += count

        for carr, counts in result.items():
            tot = counts['Total']
            for r in ['Bajo', 'Medio', 'Alto']:
                counts[r] = round((counts[r] / tot) * 100, 2)
            del counts['Total']
            
        conn.close()
        return result

    def get_work_stats(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT trabaja, riesgo_academico, COUNT(*) as count 
            FROM estudiantes 
            GROUP BY trabaja, riesgo_academico
        """)
        rows = cursor.fetchall()
        
        result = {}
        for row in rows:
            trb = row['trabaja']
            risk = row['riesgo_academico']
            count = row['count']
            if trb not in result:
                result[trb] = {'Bajo': 0, 'Medio': 0, 'Alto': 0, 'Total': 0}
            result[trb][risk] = count
            result[trb]['Total'] += count

        for trb, counts in result.items():
            tot = counts['Total']
            for r in ['Bajo', 'Medio', 'Alto']:
                counts[r] = round((counts[r] / tot) * 100, 2)
            del counts['Total']
            
        conn.close()
        return result

    def get_training_data(self):
        conn = self._get_connection()
        query = "SELECT asistencia, tareas_entregadas, horas_estudio, participacion, uso_plataforma, riesgo_academico FROM estudiantes"
        df_train = pd.read_sql_query(query, conn)
        conn.close()
        return df_train


class AcademicPredictor:
    def __init__(self):
        self.model = None
        self.features = ['asistencia', 'tareas_entregadas', 'horas_estudio', 'participacion', 'uso_plataforma']
        self.classes = ['Bajo', 'Medio', 'Alto']

    def train(self, df_train):
        print("Training decision tree model...")
        try:
            from sklearn.tree import DecisionTreeClassifier
            X = df_train[self.features]
            y = df_train['riesgo_academico']
            self.model = DecisionTreeClassifier(max_depth=4, random_state=42)
            self.model.fit(X, y)
            self.classes = list(self.model.classes_)
            print("Model trained successfully via Scikit-Learn.")
        except Exception as e:
            print(f"Machine learning training skipped (fallback to rules): {e}")
            self.model = None
        finally:
            del df_train
            gc.collect()

    def predict(self, input_data):
        asistencia = input_data['asistencia']
        tareas = input_data['tareas_entregadas']
        horas = input_data['horas_estudio']
        participacion = input_data['participacion']
        uso_plataforma = input_data['uso_plataforma']
        modalidad = input_data.get('modalidad', 'Virtual')

        if self.model is not None:
            pred_df = pd.DataFrame([[asistencia, tareas, horas, participacion, uso_plataforma]], columns=self.features)
            pred = self.model.predict(pred_df)[0]
            probs = self.model.predict_proba(pred_df)[0]
            prob_dict = {self.classes[i]: round(probs[i] * 100, 2) for i in range(len(self.classes))}
            return {'prediction': pred, 'probabilities': prob_dict}
        else:
            prob_dict = {'Bajo': 0.0, 'Medio': 0.0, 'Alto': 0.0}
            if asistencia < 62 or (modalidad in ['Virtual', 'Hibrida'] and asistencia < 72):
                prediction = 'Alto'
                prob_dict['Alto'] = 85.0
                prob_dict['Medio'] = 12.0
                prob_dict['Bajo'] = 3.0
            elif asistencia < 75 or tareas < 7:
                prediction = 'Medio'
                prob_dict['Medio'] = 75.0
                prob_dict['Alto'] = 18.0
                prob_dict['Bajo'] = 7.0
            else:
                prediction = 'Bajo'
                prob_dict['Bajo'] = 88.0
                prob_dict['Medio'] = 10.0
                prob_dict['Alto'] = 2.0
            return {'prediction': prediction, 'probabilities': prob_dict}


class ReportService:
    def __init__(self, report_path="RESUMEN_EJECUTIVO.md"):
        self.report_path = report_path

    def get_report_content(self):
        if not os.path.exists(self.report_path):
            return "El reporte ejecutivo aun no ha sido redactado."
        with open(self.report_path, "r", encoding="utf-8") as f:
            return f.read()


class QnAService:
    def __init__(self):
        self.qna_data = [
            {
                "question": "¿Como se distribuye la nota final?",
                "answer": "El promedio general es de 93.20 con una desviacion estandar de 7.50. El valor minimo registrado es 55. La distribucion esta sesgada negativamente hacia calificaciones altas, con la mitad de los estudiantes (mediana) en 95 y el 25% superior alcanzando la nota maxima de 100."
            },
            {
                "question": "¿Hay diferencias de nota final entre modalidades?",
                "answer": "Las diferencias promedio son muy leves: Hibrida (93.55), Presencial (93.30) y Virtual (92.74). Sin embargo, la modalidad Virtual presenta la menor nota promedio y la mayor dispersion (desviacion estandar de 7.72), indicando que concentra calificaciones mas heterogeneas y extremas."
            },
            {
                "question": "¿Que carrera tiene mayor promedio de nota final?",
                "answer": "Ciberseguridad registra el promedio mas alto con 93.23, seguida de cerca por Administracion con 93.20 y Data Science con 93.19. Las diferencias promedios entre todas las carreras del dataset no superan los 0.06 puntos."
            },
            {
                "question": "¿Que carrera tiene mayor variabilidad en las notas?",
                "answer": "La carrera de Finanzas presenta la mayor variabilidad con una desviacion estandar de 7.52, seguida por Data Science con 7.51. Ciberseguridad cuenta con la menor variabilidad con una desviacion estandar de 7.49."
            },
            {
                "question": "¿Existe relacion entre horas de estudio y nota final?",
                "answer": "Si, existe una relacion lineal positiva moderada-fuerte, con un coeficiente de correlacion de 0.5960. A mayores horas de estudio semanales, mayor es la calificacion final obtenida."
            },
            {
                "question": "¿Existe relacion entre asistencia y nota final?",
                "answer": "Si, existe una relacion lineal positiva debil con un coeficiente de 0.2154. Aunque su asociacion directa es debil, es la variable clave que define el desenganche y riesgo de reprobacion de los alumnos en modalidades no presenciales."
            },
            {
                "question": "¿Los estudiantes que trabajan tienen menor rendimiento?",
                "answer": "Si. Los estudiantes que no trabajan promedian 96.32 en su nota final con una desviacion de 5.32, mientras que los estudiantes que si trabajan promedian 89.37 con una desviacion de 7.99. Representa una brecha de rendimiento de casi 7 puntos porcentuales."
            },
            {
                "question": "¿Que campus concentra mayor riesgo academico?",
                "answer": "El campus Virtual concentra tanto el mayor porcentaje de alumnos en riesgo alto (12.93%) como el mayor volumen absoluto (34,410 estudiantes en riesgo alto). Los campus fisicos promedian uniformemente un 9.0% de riesgo alto."
            },
            {
                "question": "¿El uso de plataforma se asocia con mejores notas?",
                "answer": "La relacion lineal directa es sumamente debil (coeficiente de correlacion de 0.0616). Sin embargo, al segmentar por cuartiles de uso, el promedio de notas se incrementa levemente, pasando de 92.57 en el cuartil mas bajo a 93.78 en el de mayor uso."
            },
            {
                "question": "¿Que recomendacion harian a ULEAD con base en los datos?",
                "answer": "Se recomienda: 1) Activar alertas automaticas (SATA) al tutor ante caidas de asistencia abajo del 75% en virtual/hibrido. 2) Priorizar presupuesto de tutorias en el campus Virtual e Hibrido (representan el 82.44% del riesgo alto institucional). 3) Implementar entregas flexibles y tutorias asincronas para el segmento de estudiantes que trabajan, mitigando la brecha de rendimiento de 7 puntos."
            }
        ]

    def get_qna(self):
        return self.qna_data


# Initialize OOP instances
db = StudentDatabase()
predictor = AcademicPredictor()
report_service = ReportService()
qna_service = QnAService()

# Train predictor
df_temp = db.get_training_data()
predictor.train(df_temp)

@app.get("/")
def read_root():
    return FileResponse("templates/index.html")

@app.get("/api/stats")
def get_stats():
    overall = db.get_overall_stats()
    return {
        'total_students': overall['total_students'],
        'overall_risk': overall['risk_distribution'],
        'modality_risk': db.get_modality_stats(),
        'attendance_risk': db.get_attendance_stats(),
        'carrera_risk': db.get_career_stats(),
        'work_risk': db.get_work_stats()
    }

@app.post("/api/predict")
async def predict(request_data: Request):
    try:
        data = await request_data.json()
        result = predictor.predict(data)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/report")
def get_report():
    try:
        content = report_service.get_report_content()
        return {'markdown': content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/qna")
def get_qna():
    return qna_service.get_qna()

if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8585)
