from .Database import Database


class DataRepository:
    @staticmethod
    def json_or_formdata(request):
        if request.method != 'GET' and request.content_type == 'application/json':
            gegevens = request.get_json()
        else:
            gegevens = request.form.to_dict()
        return gegevens

    # vul hier de verschillende functies aan om je database aan te spreken
    @staticmethod
    def read_elements():
        sql = "SELECT * FROM elements INNER JOIN types ON elements.typeID = types.typeID ORDER BY atomicNumber"
        return Database.get_rows(sql)
    
    @staticmethod
    def read_elements_by_type(id):
        sql = "SELECT * FROM elements INNER JOIN types ON elements.typeID = types.typeID WHERE elements.typeID = %s"
        params = [id]
        return Database.get_rows(sql, params)
    
    @staticmethod
    def read_element_by_atomicnumber(id):
        sql = "SELECT * FROM elements WHERE atomicnumber= %s"
        params = [id]
        return Database.get_one_row(sql, params)
    
    @staticmethod
    def read_types():
        sql = "SELECT * FROM types"
        return Database.get_rows(sql)
    
    @staticmethod
    def read_type_by_id(id):
        sql = "SELECT * FROM types WHERE typeid = %s"
        params = [id]
        return Database.get_one_row(sql, params)
    
    @staticmethod
    def read_types_by_zoekstring(zoekstring):
        sql = "SELECT * FROM types WHERE type LIKE %s"
        params = [zoekstring + "%"]
        return Database.get_rows(sql, params)
    @staticmethod
    def read_jaartallen():
        sql = "SELECT DISTINCT yearDiscovered FROM elements WHERE yearDiscovered > 1800 ORDER BY yearDiscovered ASC"
        return Database.get_rows(sql)
    @staticmethod
    def create_type(code, type):
        sql = "INSERT INTO types (typeCode, type) VALUES (%s,%s)"
        params = [code, type]
        return Database.execute_sql(sql, params)
    
    @staticmethod
    def update_type(id, code):
        sql = "UPDATE types g SET g.typeCode = %s WHERE typeID = %s"
        params = [code, id]
        return Database.execute_sql(sql, params)
