import threatingestor.artifacts
from threatingestor.operators import Operator
from threatingestor.exceptions import DependencyError


try:
    import pymysql
except ImportError:
    raise DependencyError("Dependency pymysql required for MySQL operator is not installed")


class Plugin(Operator):
    """Operator for MySQL."""
    def __init__(self, host, database, table, user=None, password='', port=3306,
                 artifact_types=None, filter_string=None, allowed_sources=None):
        """MySQL operator."""
        super(Plugin, self).__init__(artifact_types, filter_string, allowed_sources)
        self.artifact_types = artifact_types or [
            threatingestor.artifacts.Domain,
            threatingestor.artifacts.Hash,
            threatingestor.artifacts.IPAddress,
            threatingestor.artifacts.URL,
            threatingestor.artifacts.YARASignature,
            threatingestor.artifacts.Task,
        ]

        # Connect to SQL and set up the tables if they aren't already.
        self.sql = pymysql.connect(host=host, port=port, user=user,
                                   password=password, database=database)
        self.table = table
        self.cursor = self.sql.cursor()

        self._create_table()


    def _create_table(self):
        """Create the table defined in the config if it does not already exist."""
        query = f"""
            CREATE TABLE IF NOT EXISTS `{self.table}` (
                `artifact` TEXT PRIMARY KEY,
                `reference_link` TExT,
                `reference_text` TEXT,
                `created_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
                `state` TEXT
            ) 
        """
        self.cursor.execute(query)
        self.sql.commit()


    def _insert_artifact(self, artifact):
        """Insert the given artifact into the table."""
        type_name = artifact.__class__.__name__.lower()
        query = f"""
            INSERT IGNORE INTO `{self.table}` (
                `artifact`,
                `artifact_type`,
                `reference_link`,
                `reference_text`,
                `created_date`,
                `state`
            )
            VALUES (?, ?, ?, ?, datetime('now', 'utc'), NULL)
        """
        self.cursor.execute(query, (
            str(artifact),
            type_name,
            artifact.reference_link,
            artifact.reference_text
        ))
        self.sql.commit()


    def handle_artifact(self, artifact):
        """Operate on a single artifact."""
        self._insert_artifact(artifact)
