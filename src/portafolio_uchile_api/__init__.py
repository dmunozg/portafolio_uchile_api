import requests, json, math


def extract_academicos(jsonData):
    academicosDict = {}
    for academic in jsonData:
        academicID = academic["id_persona"]
        academicosDict[academicID] = {
            "nombres": academic["nombres"],
            "paterno": academic["paterno"],
            "materno": academic["materno"],
            "nombre_completo": academic["nombre_completo"],
            "email": academic["correo"],
        }
    return academicosDict


class PortafolioAPI:
    def __init__(self, base_url):
        self.base_url = base_url
        self.headers = headers = {
            "Origin": "https://uchile.cl",
            "Referer": "https://uchile.cl/",
            "User-Agent": "AnuarioCiencias (pepmimlab.com; mailto:diego.munoz.g@ug.uchile.cl)",
            "sec-ch-ua": '"Not/A)Brand";v="99", "Microsoft Edge";v="115", "Chromium";v="115"',
        }

    def query_unidades(self):
        response = requests.request(
            "GET",
            self.base_url + "/lista/unidades",
            headers=self.headers,
            data={},
        )
        if response.status_code != 200:
            print(f"Error {response.status_code}")
            return None
        units = {}
        for unit in response.json()["data"]:
            unitID = unit["id"]
            unitName = unit["nombre"]
            units[unitID] = unitName
        return units

    def query_departamentos(self, unitID):
        response = requests.request(
            "GET",
            self.base_url + f"/lista/departamento?unidad={unitID}",
            headers=self.headers,
            data={},
        )
        if response.status_code != 200:
            print(f"Error {response.status_code}")
            return None
        depts = {}
        for dept in response.json()["data"]["departamentos"]:
            deptID = dept["id"]
            deptName = dept["nombre"]
            depts[deptID] = deptName
        return depts

    def query_academicos(self, deptID):
        response = requests.request(
            "GET",
            self.base_url + f"/lista/por_reparticion?departamento={deptID}",
            headers=self.headers,
            data={},
        )
        academicosDict = extract_academicos(response.json()["data"]["academicos"])
        # Indentificar número total de académicos
        nAcademicos = response.json()["data"]["total_resultado"]
        # Identificar el número de páginas que se debe extraer
        nPags = math.ceil(nAcademicos / 12)
        if nPags == 1:
            # Ya esta toda la información
            return academicosDict
        else:
            # Falta por consultar más páginas
            for page in range(nPags - 1):  # -1 porque la primera ya se consultó
                response = requests.request(
                    "GET",
                    self.base_url
                    + f"/lista/por_reparticion?departamento={deptID}&pagina={page+2}",
                    headers=self.headers,
                    data={},
                )
                academicosDict.update(
                    extract_academicos(response.json()["data"]["academicos"])
                )
            return academicosDict

    def query_publicaciones(self, academicoID):
        response = requests.request(
            "GET",
            self.base_url + f"/publicaciones?id_persona={academicoID}",
            headers=self.headers,
            data={},
        )
        if response.status_code != 200:
            print(f"Error {response.status_code}")
            return None
        return response.json()["data"]["academicos"][0]["publicaciones"]

    def query_proyectos(self, academicoID):
        response = requests.request(
            "GET",
            self.base_url + f"/proyectos?id_persona={academicoID}",
            headers=self.headers,
            data={},
        )
        if response.status_code != 200:
            print(f"Error {response.status_code}")
            return None
        return response.json()["data"]["academicos"]["proyectos"]
