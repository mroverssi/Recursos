CREATE TABLE  fecha (
    fecha_key INT NOT NULL,
    ano VARCHAR(255),
    mes VARCHAR(255),
    PRIMARY KEY(fecha_key)
);

CREATE TABLE empresa (
    empresa_key INT NOT NULL,
    empresa VARCHAR(255),
    PRIMARY KEY(empresa_key)
)

CREATE TABLE tipo_de_vuelo (
    tipo_de_vuelo_key INT NOT NULL,
    tipo_vuelo VARCHAR(255),
    PRIMARY KEY(tipo_vuelo_key)
)

CREATE TABLE trafico (
    trafico_key INT NOT NULL,
    trafico VARCHAR(255),
    PRIMARY KEY(trafico_key)
)

CREATE TABLE aeropuertos (
    aeropuertos_key INT NOT NULL,
    iata VARCHAR(255),
	sigla VARCHAR(255),
	nombre VARCHAR(255),
	clase VARCHAR(255),
	propietario VARCHAR(255),
	explotador VARCHAR(255),
	resolucion VARCHAR(255),
	fecha_construccion DATE,
	fecha_vigencia DATE,
	ano VARCHAR(255),
	elevacion FLOAT,
	numero_vuelos_origen FLOAT,
    departamento VARCHAR(255),
    municipio VARCHAR(255),
    categoria VARCHAR(255),
    latitud FLOAT,
    longitud FLOAT,
    tipo VARCHAR(255),
	pmbo FLOAT,
	estado_actual VARCHAR(255)
	fecha_vigencia_inicial DATE,
	fecha_vigencia_final DATE,
    PRIMARY KEY(aeropuertos_key)
)
CREATE TABLE tipo_equipo (
    tipo_equipo_key INT NOT NULL,
    tipo_aeronave VARCHAR(255),
	EngineCount FLOAT,
	numero_motores INT,
	fabricante VARCHAR(255),
	WTC VARCHAR(255),
    PRIMARY KEY(tipo_equipo_key)
)
CREATE TABLE fact_vuelos (
    vuelos_key INT NOT NULL,
    vuelos INT,
    sillas INT,
    pasajeros INT,
    carga_ofrecida FLOAT,
    carga_bordo FLOAT,
    fecha_key INT,
    empresa_key INT,
    tipo_vuelo_key INT,
    trafico_key INT,
    origen_key INT,
    destino_key INT,
	tipo_equipo_key INT,
    PRIMARY KEY(vuelos_key),
    FOREIGN KEY (fecha_key) REFERENCES fecha(fecha_key),
    FOREIGN KEY (empresa_key) REFERENCES empresa(empresa_key),
    FOREIGN KEY (tipo_de_vuelo_key) REFERENCES tipo_de_vuelo(tipo_de_vuelo_key),
    FOREIGN KEY (trafico_key) REFERENCES trafico(trafico_key),
    FOREIGN KEY (origen_key) REFERENCES aeropuertos(aeropuertos_key),
    FOREIGN KEY (destino_key) REFERENCES aeropuertos(aeropuertos_key),
	FOREIGN KEY (tipo_equipo_key) REFERENCES tipo_equipo(tipo_equipo_key),
	
)