import firebase_admin
from firebase_admin import credentials, firestore
from typing import Optional
import os


class FirebaseService:
    _instance = None
    _db = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._db is None:
            self._initialize_firebase()

    def _initialize_firebase(self):
        """Inicializa la conexión con Firebase"""
        try:
            # Verificar si ya existe una app inicializada
            firebase_admin.get_app()
        except ValueError:
            # Si no existe, inicializar
            cred_path = os.getenv(
                "FIREBASE_CREDENTIALS_PATH",
                "secrets/cuentas/firebase-credentials.json"
            )
            
            if os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
            else:
                # Inicialización sin credenciales para desarrollo local
                firebase_admin.initialize_app()

        self._db = firestore.client()

    @property
    def db(self):
        """Retorna la instancia de Firestore"""
        if self._db is None:
            self._initialize_firebase()
        return self._db

    def get_collection(self, collection_name: str):
        """Obtiene una referencia a una colección"""
        return self.db.collection(collection_name)

    def get_document(self, collection_name: str, doc_id: str):
        """Obtiene un documento específico"""
        return self.db.collection(collection_name).document(doc_id)

    def create_document(self, collection_name: str, data: dict, doc_id: Optional[str] = None):
        """Crea un nuevo documento"""
        collection_ref = self.db.collection(collection_name)
        
        if doc_id:
            doc_ref = collection_ref.document(doc_id)
            doc_ref.set(data)
            return doc_id
        else:
            doc_ref = collection_ref.add(data)
            return doc_ref[1].id

    def update_document(self, collection_name: str, doc_id: str, data: dict):
        """Actualiza un documento existente"""
        doc_ref = self.db.collection(collection_name).document(doc_id)
        doc_ref.update(data)

    def delete_document(self, collection_name: str, doc_id: str):
        """Elimina un documento"""
        doc_ref = self.db.collection(collection_name).document(doc_id)
        doc_ref.delete()

    def query_documents(self, collection_name: str, filters: list = None):
        """
        Realiza una consulta con filtros
        filters: lista de tuplas (campo, operador, valor)
        Ejemplo: [('estado', '==', 'ACTIVA'), ('saldo', '>', 1000)]
        """
        query = self.db.collection(collection_name)
        
        if filters:
            for field, operator, value in filters:
                query = query.where(field, operator, value)
        
        return query.stream()


# Instancia global del servicio
firebase_service = FirebaseService()


def get_firebase_db():
    """Dependency para FastAPI"""
    return firebase_service.db