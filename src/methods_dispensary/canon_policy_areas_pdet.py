# ============================================================================
# CANONICAL CONSTANTS FROM GUIDES - PDET-Focused Policy Areas
# ============================================================================
# Source: questionnaire_monolith.json + PDET/territorial planning methodology
# All parameters are deterministic and traceable to official DNP/SisPT guides
# ============================================================================

MICRO_LEVELS = {
    "EXCELENTE": 0.85,
    "BUENO": 0.70,
    "ACEPTABLE": 0.55,
    "INSUFICIENTE": 0.00
}

CANON_POLICY_AREAS = {
    "PA01": {
        "name": "Derechos de las mujeres e igualdad de género",
        "legacy": "P1",
        "pdet_focus": "Mujeres rurales, víctimas del conflicto y liderazgo femenino en territorios PDET",
        "keywords": [
            # Core concepts
            "género", "mujer", "mujeres", "igualdad de género", "equidad de género",
            "mujeres rurales", "campesinas", "mujeres indígenas", "mujeres afrodescendientes",
            
            # Violence and protection - PDET context
            "violencia basada en género", "VBG", "feminicidio", "violencia intrafamiliar",
            "violencia sexual", "violencia económica", "violencia psicológica",
            "violencia sexual en el conflicto", "violencia de género en zonas rurales",
            "ruta de atención VBG rural", "casas de justicia", "comisarías de familia rural",
            
            # Economic rights - Rural focus
            "brecha salarial", "participación laboral", "emprendimiento femenino",
            "economía del cuidado", "trabajo no remunerado",
            "proyectos productivos mujeres", "asociaciones de mujeres", "cooperativas femeninas",
            "acceso a crédito rural", "fondo de mujeres", "empoderamiento económico",
            "mujeres cabeza de familia", "jefatura femenina hogar",
            
            # Political participation - Territorial
            "participación política", "liderazgo femenino", "paridad", "cuotas de género",
            "consejos comunitarios", "JAC", "Juntas de Acción Comunal",
            "mesas de mujeres", "organizaciones de mujeres", "redes de mujeres",
            "veeduría ciudadana", "control social", "presupuestos participativos",
            
            # Health and rights - Rural context
            "salud sexual y reproductiva", "derechos reproductivos", "mortalidad materna",
            "parto humanizado", "partería tradicional", "medicina ancestral",
            "atención prenatal rural", "planificación familiar", "IVE",
            "salud mental mujeres", "atención psicosocial",
            
            # Land and property rights
            "acceso a tierras", "titulación predios", "adjudicación tierras mujeres",
            "baldíos", "UAF", "Unidades Agrícolas Familiares",
            
            # PDET-specific
            "PATR", "Planes de Acción para la Transformación Regional",
            "iniciativas PDET género", "pilares PDET", "ART", "Agencia de Renovación del Territorio",
            
            # Data sources
            "DANE", "Medicina Legal", "SIVIGILA", "SISPRO", "Fiscalía",
            "censo agropecuario", "terridata", "sistema de información PDET"
        ]
    },
    
    "PA02": {
        "name": "Prevención de la violencia y protección de la población frente al conflicto armado y la violencia generada por grupos delincuenciales organizados, asociada a economías ilegales",
        "legacy": "P2",
        "pdet_focus": "Prevención en territorios post-acuerdo, alertas tempranas y protección comunitaria",
        "keywords": [
            # Conflict and violence - Post-agreement
            "conflicto armado", "violencia", "prevención", "protección",
            "post-conflicto", "post-acuerdo", "implementación del acuerdo de paz",
            "territorios PDET", "municipios PDET", "subregiones PDET",
            
            # Armed groups and violence
            "grupos armados organizados", "GAO", "grupos de delincuencia organizada", "GDO",
            "disidencias", "estructuras armadas", "economías ilícitas",
            "narcotráfico", "cultivos ilícitos", "coca", "sustitución voluntaria", "PNIS",
            "minería ilegal", "extorsión", "control territorial",
            
            # Human rights violations
            "derechos humanos", "DIH", "derecho internacional humanitario",
            "violaciones a derechos humanos", "crímenes de guerra",
            "masacres", "desplazamiento forzado", "confinamiento",
            "reclutamiento forzado", "minas antipersona", "MAP", "MUSE",
            
            # Early warning - Territorial
            "alertas tempranas", "SAT", "sistema de alertas", "riesgo",
            "informes de riesgo", "notas de seguimiento", "Defensoría del Pueblo",
            "comités territoriales de prevención", "planes de contingencia",
            "mapeo de riesgos", "análisis de contexto",
            
            # Protection mechanisms
            "medidas de protección", "rutas de protección", "UNP",
            "protección colectiva", "planes de protección comunitaria",
            "guardias indígenas", "guardias cimarronas", "guardias campesinas",
            "autoprotección", "sistema de protección territorial",
            
            # Victims and vulnerable populations
            "víctimas", "afectados", "población vulnerable",
            "desplazados", "comunidades étnicas", "campesinos",
            
            # Institutions and programs
            "CIAT", "Comisión Intersectorial de Alertas Tempranas",
            "CIPRAT", "consejos de seguridad", "fuerza pública",
            "Policía comunitaria", "Ejército"
        ]
    },
    
    "PA03": {
        "name": "Ambiente sano, cambio climático, prevención y atención a desastres",
        "legacy": "P3",
        "pdet_focus": "Sostenibilidad ambiental rural, ordenamiento territorial y gestión de riesgos",
        "keywords": [
            # Environmental rights - Rural context
            "ambiente sano", "medio ambiente", "ambiental", "sostenible", "sostenibilidad",
            "economía campesina sostenible", "agroecología", "sistemas agroforestales",
            "bioeconomía", "negocios verdes", "cadenas de valor sostenibles",
            
            # Climate change - Territorial impact
            "cambio climático", "adaptación climática", "mitigación", "emisiones",
            "gases de efecto invernadero", "carbono neutral",
            "variabilidad climática", "sequías", "inundaciones",
            "seguridad hídrica", "estrés hídrico",
            
            # Ecosystems - Strategic regions
            "ecosistemas", "biodiversidad", "conservación", "áreas protegidas",
            "páramos", "humedales", "bosques", "selva", "Amazonía",
            "corredores biológicos", "reservas naturales", "zonas de amortiguación",
            "deforestación", "restauración ecológica", "reforestación",
            
            # Illegal activities impact
            "cultivos ilícitos impacto ambiental", "aspersión", "glifosato",
            "minería ilegal", "contaminación por mercurio", "afectación de fuentes hídricas",
            "tala ilegal", "tráfico de fauna", "pesca ilegal",
            
            # Disasters - Rural vulnerability
            "desastres", "gestión del riesgo", "prevención de desastres",
            "atención de emergencias", "resiliencia",
            "deslizamientos", "avalanchas", "crecientes súbitas",
            "incendios forestales", "temporada seca", "temporada de lluvias",
            "POMCA", "planes de ordenamiento de cuencas",
            
            # Water and resources - Rural access
            "recursos hídricos", "cuencas", "agua potable", "saneamiento básico",
            "acueductos comunitarios", "acueductos veredales", "pozos",
            "sistemas de abastecimiento rural", "tratamiento de aguas",
            "alcantarillado rural", "soluciones individuales",
            
            # PDET-specific
            "pilar ambiental PDET", "planes de manejo ambiental",
            "guardabosques", "familias guardabosques",
            
            # Institutions
            "CAR", "CRC", "Corporación Autónoma Regional", "IDEAM", "MinAmbiente",
            "Parques Nacionales Naturales", "UNGRD", "consejos de cuenca",
            "consejos municipales de gestión del riesgo", "CMGRD"
        ]
    },
    
    "PA04": {
        "name": "Derechos económicos, sociales y culturales",
        "legacy": "P4",
        "pdet_focus": "Infraestructura rural, servicios básicos y desarrollo económico territorial",
        "keywords": [
            # Economic rights - Rural development
            "derechos económicos", "DESC", "desarrollo económico", "empleo", "trabajo decente",
            "economía campesina", "agricultura familiar", "pequeños productores",
            "desarrollo rural integral", "economía solidaria", "cooperativas",
            "asociatividad", "encadenamientos productivos",
            
            # Rural infrastructure - Critical needs
            "infraestructura", "vías", "conectividad", "transporte", "movilidad",
            "vías terciarias", "vías rurales", "caminos veredales", "puentes",
            "placa huella", "mantenimiento vial", "maquinaria amarilla",
            "accesibilidad rural", "integración territorial",
            
            # Basic services - Rural coverage
            "servicios básicos", "acueducto", "alcantarillado", "energía eléctrica",
            "gas natural", "telecomunicaciones", "internet",
            "electrificación rural", "energías alternativas", "paneles solares",
            "conectividad digital", "puntos vive digital", "zonas wifi",
            "telefonía móvil", "cobertura rural",
            
            # Social rights - Rural context
            "salud", "educación", "vivienda", "seguridad social",
            "salud rural", "puestos de salud", "centros de salud rural",
            "IPS", "EPS", "régimen subsidiado", "ARL",
            "educación rural", "escuelas rurales", "colegios agropecuarios",
            "transporte escolar", "alimentación escolar", "PAE",
            "jornada única", "etnoeducación", "pedagogías rurales",
            "vivienda rural", "mejoramiento de vivienda", "saneamiento básico vivienda",
            "materiales locales", "vivienda digna",
            
            # Agricultural development
            "asistencia técnica", "extensión agropecuaria", "EPSEA",
            "adecuación de tierras", "distritos de riego", "infraestructura productiva",
            "centros de acopio", "plantas de transformación", "agroindustria rural",
            "comercialización", "mercados campesinos", "compras públicas",
            
            # Financial inclusion
            "inclusión financiera", "crédito rural", "FINAGRO", "Banco Agrario",
            "microcrédito", "fondos rotatorios", "garantías",
            
            # Cultural rights - Territorial identity
            "cultura", "patrimonio cultural", "identidad cultural", "diversidad cultural",
            "cultura campesina", "saberes ancestrales", "patrimonio inmaterial",
            "casas de cultura", "bibliotecas rurales", "escenarios culturales",
            "fiestas tradicionales", "gastronomía regional",
            
            # Food security - Territorial
            "seguridad alimentaria", "soberanía alimentaria", "nutrición",
            "autosuficiencia alimentaria", "huertas caseras", "seguridad nutricional",
            "desnutrición infantil", "malnutrición",
            
            # PDET-specific
            "PATR componente infraestructura", "obras por impuestos",
            "catastro multipropósito", "formalización empresarial",
            
            # Institutions
            "MinSalud", "MinEducación", "MinVivienda", "MinTransporte",
            "MinAgricultura", "ADR", "Agencia de Desarrollo Rural",
            "INVIAS", "IPSE", "MinTIC"
        ]
    },
    
    "PA05": {
        "name": "Derechos de las víctimas y construcción de paz",
        "legacy": "P5",
        "pdet_focus": "Reparación integral, retornos y construcción de paz territorial",
        "keywords": [
            # Victims' rights - Comprehensive
            "víctimas", "derechos de las víctimas", "reparación", "indemnización",
            "restitución", "rehabilitación", "satisfacción", "garantías de no repetición",
            "registro único de víctimas", "RUV", "caracterización de víctimas",
            "enfoque diferencial", "enfoque de género", "enfoque étnico",
            
            # Types of victimization
            "desplazamiento forzado", "despojo de tierras", "abandono forzado",
            "homicidio", "desaparición forzada", "secuestro", "tortura",
            "violencia sexual", "reclutamiento forzado", "minas antipersona",
            "masacres", "ataques a poblaciones", "confinamiento",
            
            # Return and relocation
            "retornos", "reubicaciones", "reasentamientos",
            "planes de retorno", "acompañamiento al retorno", "garantías de seguridad",
            "reconstrucción del proyecto de vida", "estabilización socioeconómica",
            
            # Peacebuilding - Territorial
            "construcción de paz", "paz territorial", "reconciliación", "convivencia",
            "perdón", "memoria histórica", "pedagogía de la paz",
            "culturas de paz", "resolución pacífica de conflictos",
            "pactos de convivencia", "planes de convivencia",
            
            # Psychosocial support
            "atención psicosocial", "acompañamiento psicosocial", "PAPSIVI",
            "salud mental", "trauma", "duelo", "sanación colectiva",
            "estrategia de recuperación emocional", "grupos de apoyo mutuo",
            
            # Truth and justice
            "verdad", "justicia", "justicia transicional", "JEP",
            "Jurisdicción Especial para la Paz", "CEV", "Comisión de la Verdad",
            "búsqueda de desaparecidos", "UBPD", "exhumaciones",
            "sentencias", "macrocasos", "reconocimiento de responsabilidad",
            
            # Memory and non-repetition
            "memoria histórica", "lugares de memoria", "museos de memoria",
            "iniciativas de memoria", "archivos de memoria",
            "monumentos", "conmemoraciones", "actos de reconocimiento",
            "garantías de no repetición", "reformas institucionales",
            
            # Community participation
            "participación de víctimas", "mesas de víctimas", "organizaciones de víctimas",
            "redes de víctimas", "voceros de víctimas",
            "planes de reparación colectiva", "sujetos de reparación colectiva",
            
            # Land restitution
            "restitución de tierras", "Unidad de Restitución",
            "jueces de restitución", "sentencias de restitución",
            "formalización de predios restituidos", "proyectos productivos post-restitución",
            
            # PDET-specific
            "territorios de paz", "laboratorios de paz",
            "PDET como mecanismo de reparación", "transformación territorial",
            
            # Institutions
            "Unidad de Víctimas", "UARIV", "Fiscalía", "Defensoría del Pueblo",
            "CNMH", "Centro Nacional de Memoria Histórica",
            "Sistema Integral de Verdad, Justicia, Reparación y No Repetición", "SIVJRNR"
        ]
    },
    
    "PA06": {
        "name": "Derecho al buen futuro de la niñez, adolescencia, juventud y entornos protectores",
        "legacy": "P6",
        "pdet_focus": "Protección de niñez rural, prevención de reclutamiento y oportunidades para jóvenes",
        "keywords": [
            # Children and adolescents - Rural context
            "niñez", "niños", "niñas", "adolescencia", "adolescentes",
            "primera infancia", "infancia",
            "niñez rural", "infancia campesina", "niños indígenas", "niños afrodescendientes",
            
            # Protection - Conflict-affected areas
            "protección integral", "derechos de la niñez", "interés superior del niño",
            "prevención de violencia", "abuso infantil", "explotación sexual",
            "prevención de reclutamiento", "reclutamiento forzado", "utilización de niños",
            "niños víctimas del conflicto", "niños desvinculados",
            "rutas de protección rural", "comisarías de familia",
            "sistema de responsabilidad penal adolescente", "SRPA",
            
            # Development - Rural needs
            "desarrollo integral", "educación", "salud infantil", "nutrición infantil",
            "estimulación temprana", "desarrollo cognitivo",
            "centros de desarrollo infantil", "CDI", "hogares comunitarios",
            "jardines sociales", "atención integral primera infancia",
            "educación inicial", "transiciones educativas",
            "desnutrición crónica", "bajo peso al nacer", "retardo en talla",
            "lactancia materna", "complementación alimentaria",
            
            # Education - Rural context
            "educación rural", "escuela nueva", "modelos flexibles",
            "transporte escolar", "internados", "residencias escolares",
            "alimentación escolar", "PAE", "útiles escolares",
            "deserción escolar", "repitencia", "analfabetismo",
            "educación media", "articulación con educación superior",
            
            # Youth - Opportunities and participation
            "juventud", "jóvenes", "adolescentes y jóvenes",
            "jóvenes rurales", "juventud campesina",
            "participación juvenil", "consejos de juventud", "voz de los jóvenes",
            "plataformas juveniles", "organizaciones juveniles",
            "liderazgo juvenil", "formación política juvenil",
            
            # Opportunities - Economic and social
            "oportunidades", "empleabilidad juvenil", "emprendimiento juvenil",
            "formación para el trabajo", "SENA rural", "técnica", "tecnológica",
            "primer empleo", "pasantías rurales", "experiencia laboral",
            "proyectos productivos juveniles", "relevo generacional",
            "acceso a tierras jóvenes", "arraigo rural",
            
            # Recreation and culture
            "recreación", "deporte", "cultura", "tiempo libre",
            "escuelas deportivas", "ludotecas", "bibliotecas",
            "acceso a tecnología", "alfabetización digital",
            
            # Mental health and substance abuse
            "salud mental juvenil", "prevención de suicidio",
            "prevención de consumo de sustancias", "farmacodependencia",
            "embarazo adolescente", "prevención de embarazo temprano",
            "educación sexual", "proyectos de vida",
            
            # PDET-specific
            "estrategia para niñez y adolescencia PDET",
            "jóvenes constructores de paz", "semilleros de paz",
            
            # Institutions
            "ICBF", "Instituto Colombiano de Bienestar Familiar",
            "Comisarías de Familia", "Defensorías de Familia",
            "Ministerio de Educación", "Secretarías de Educación",
            "Colombia Joven", "Sistema Nacional de Juventud"
        ]
    },
    
    "PA07": {
        "name": "Tierras y territorios",
        "legacy": "P7",
        "pdet_focus": "Acceso, formalización, ordenamiento territorial y catastro multipropósito",
        "keywords": [
            # Land rights - Rural focus
            "tierras", "territorio", "territorial", "ordenamiento territorial",
            "uso del suelo", "tenencia de la tierra", "propiedad rural",
            "derecho a la tierra", "función social de la propiedad",
            "pequeña propiedad", "mediana propiedad", "UAF",
            
            # Land distribution and access
            "acceso a tierras", "redistribución", "reforma agraria integral",
            "fondo de tierras", "adjudicación de baldíos", "baldíos",
            "extinción de dominio", "tierras inexplotadas",
            "concentración de la tierra", "latifundio", "minifundio",
            
            # Formalization
            "formalización de la propiedad", "titulación", "saneamiento de títulos",
            "clarificación de la propiedad", "procedimientos agrarios",
            "registro de tierras", "inscripción en registro",
            "escrituración", "notarías", "costo de formalización",
            
            # Planning - Municipal and rural
            "POT", "Plan de Ordenamiento Territorial", "PBOT", "EOT",
            "esquema de ordenamiento territorial", "plan básico de ordenamiento",
            "zonificación", "usos del suelo", "clasificación del suelo",
            "suelo rural", "suelo de expansión", "suelo de protección",
            "suelo suburbano", "centros poblados", "áreas urbanas",
            "conflictos de uso del suelo", "aptitud del suelo",
            
            # Cadastre - Multipurpose
            "catastro", "gestión catastral", "actualización catastral", "avalúo catastral",
            "catastro multipropósito", "barrido predial", "censo predial",
            "información catastral", "formación catastral",
            "impuesto predial", "base gravable", "estratificación rural",
            
            # Land restitution - Post-conflict
            "restitución de tierras", "despojo", "abandono forzado",
            "Unidad de Restitución de Tierras", "URT",
            "jueces de restitución", "oposiciones", "falsas tradiciones",
            "micro-focalización", "caracterización de predios",
            "protección jurídica", "protección material",
            
            # Rural development - Territorial
            "desarrollo rural", "acceso a factores productivos",
            "infraestructura rural", "servicios rurales",
            "centros regionales", "articulación urbano-rural",
            "sistemas de ciudades", "mercados regionales",
            
            # Indigenous and afro territories
            "territorios étnicos", "resguardos indígenas", "territorios colectivos",
            "consejos comunitarios", "títulos colectivos",
            "consulta previa", "consentimiento previo libre e informado",
            "autonomía territorial", "gobierno propio", "autoridades tradicionales",
            "planes de vida", "planes de etnodesarrollo",
            "ampliación de resguardos", "saneamiento de resguardos",
            
            # Land conflicts
            "conflictos agrarios", "conflictos por tierras",
            "disputas territoriales", "ocupación irregular",
            "invasiones", "desalojos", "legalización de asentamientos",
            
            # Environmental zoning
            "áreas protegidas", "zonas de reserva forestal",
            "sustracción de reservas", "zonificación ambiental",
            "ordenamiento productivo", "sistemas agroforestales",
            
            # PDET-specific
            "pilar tierras PDET", "ordenamiento social de la propiedad",
            "cierre de la frontera agrícola", "ZRC", "Zonas de Reserva Campesina",
            
            # Institutions
            "ANT", "Agencia Nacional de Tierras",
            "IGAC", "Instituto Geográfico Agustín Codazzi",
            "Superintendencia de Notariado y Registro",
            "UPRA", "Unidad de Planificación Rural Agropecuaria",
            "DNP", "Ministerio de Agricultura"
        ]
    },
    
    "PA08": {
        "name": "Líderes y lideresas, defensores y defensoras de derechos humanos, comunitarios, sociales, ambientales, de la tierra, el territorio y de la naturaleza",
        "legacy": "P8",
        "pdet_focus": "Protección de líderes sociales y comunitarios en territorios PDET",
        "keywords": [
            # Leaders and defenders - Rural context
            "líderes sociales", "liderazgo social", "defensores de derechos humanos",
            "defensores", "activistas", "líderes comunitarios",
            "líderes rurales", "líderes campesinos", "líderes veredales",
            "presidentes de JAC", "líderes de organizaciones sociales",
            
            # Types of leaders - Specific
            "líderes ambientales", "líderes indígenas", "líderes afrodescendientes",
            "líderes de restitución", "líderes de sustitución de cultivos",
            "líderes de víctimas", "líderes de mujeres",
            "líderes comunales", "voceros comunitarios",
            "defensores de territorio", "guardias indígenas líderes",
            
            # Threats and violence - Systematic
            "amenazas", "asesinatos", "homicidios", "agresiones", "intimidación",
            "hostigamiento", "estigmatización", "señalamiento",
            "seguimientos", "vigilancia", "presiones", "extorsión",
            "desplazamiento de líderes", "exilio interno",
            "atentados", "sicariato", "violencia sistemática",
            
            # Risk factors
            "territorios de alto riesgo", "zonas rojas", "corredores estratégicos",
            "presencia de grupos armados", "economías ilícitas",
            "conflictos territoriales", "megaproyectos",
            "oposición a proyectos extractivos",
            
            # Protection - Comprehensive
            "protección", "medidas de protección", "esquemas de seguridad",
            "rutas de protección", "UNP", "Unidad Nacional de Protección",
            "medidas individuales", "medidas colectivas",
            "chaleco antibalas", "vehículo blindado", "escoltas",
            "medios de comunicación", "botones de pánico",
            "reubicación temporal", "traslados",
            
            # Community protection
            "protección colectiva", "planes de protección comunitaria",
            "autoprotección", "protección territorial",
            "sistemas comunitarios de alerta temprana",
            "redes de protección", "acompañamiento internacional",
            
            # Prevention
            "prevención", "alertas tempranas", "análisis de riesgo", "mapeo de riesgos",
            "caracterización de amenazas", "planes de contingencia",
            "protocolos de seguridad", "cultura de seguridad",
            "evaluaciones de riesgo", "rutas de evacuación",
            
            # Justice and accountability
            "investigación", "judicialización", "impunidad", "Fiscalía",
            "Fiscalía especializada", "investigaciones efectivas",
            "esclarecimiento", "identificación de autores",
            "garantías de no repetición", "sanciones",
            "justicia para líderes asesinados",
            
            # Institutional response
            "comisión intersectorial", "planes de acción oportuna", "PAO",
            "sistema de prevención y alerta", "articulación institucional",
            "presencia institucional", "fortalecimiento institucional local",
            
            # Participation guarantees
            "garantías para la participación", "espacios seguros",
            "protección de procesos organizativos",
            "libertad de expresión", "libertad de asociación",
            "derecho a la protesta", "movilización social",
            
            # Documentation and monitoring
            "registro de agresiones", "bases de datos", "observatorios",
            "monitoreo de situación", "informes de riesgo",
            "documentación de casos", "sistemas de información",
            
            # PDET-specific
            "líderes PDET", "implementadores del acuerdo",
            "defensores de la paz", "constructores de paz",
            
            # Institutions
            "Defensoría del Pueblo", "Procuraduría", "Fiscalía General",
            "Unidad Nacional de Protección", "UNP",
            "Ministerio del Interior", "Comisión Nacional de Garantías de Seguridad",
            "OACNUDH", "Oficina del Alto Comisionado ONU DDHH",
            "ONG de derechos humanos", "organizaciones internacionales"
        ]
    },
    
    "PA09": {
        "name": "Crisis de derechos de personas privadas de la libertad",
        "legacy": "P9",
        "pdet_focus": "Condiciones carcelarias y alternativas de justicia en zonas rurales",
        "keywords": [
            # Prison population
            "población privada de la libertad", "PPL", "personas privadas",
            "reclusos", "internos", "detenidos", "condenados", "sindicados",
            "presos políticos", "prisioneros de guerra",
            
            # Facilities - Regional
            "cárcel", "centro penitenciario", "establecimiento carcelario",
            "INPEC", "Instituto Nacional Penitenciario y Carcelario",
            "cárceles regionales", "cárceles municipales", "estaciones de policía",
            "centros de reclusión", "pabellones", "patios",
            
            # Crisis - Structural problems
            "hacinamiento", "sobrepoblación carcelaria", "crisis carcelaria",
            "condiciones inhumanas", "violación de derechos",
            "trato cruel", "tortura", "tratos degradantes",
            "motines", "disturbios", "incendios", "emergencias carcelarias",
            
            # Rights violations
            "derechos humanos", "dignidad humana", "salud en prisión",
            "alimentación", "visitas", "comunicación",
            "derecho a la salud", "atención médica", "medicamentos",
            "enfermedades", "tuberculosis", "VIH", "enfermedades crónicas",
            "salud mental en prisión", "suicidios", "autolesiones",
            "hacinamiento y salud", "condiciones sanitarias",
            
            # Vulnerable groups
            "mujeres privadas de la libertad", "madres gestantes", "madres lactantes",
            "niños en prisión", "adultos mayores", "población LGBTI",
            "personas con discapacidad", "enfermos terminales",
            "indígenas privados de libertad", "enfoque diferencial",
            
            # Reintegration
            "resocialización", "rehabilitación", "reinserción social",
            "programas de tratamiento", "educación en prisión", "trabajo penitenciario",
            "redención de pena", "beneficios administrativos",
            "preparación para la libertad", "pos-penados",
            "acompañamiento post-carcelario", "seguimiento",
            
            # Justice - Alternatives
            "justicia", "debido proceso", "medidas alternativas", "prisión domiciliaria",
            "vigilancia electrónica", "mecanismos sustitutivos",
            "detención preventiva", "hacinamiento por sindicados",
            "justicia restaurativa", "conciliación",
            "descongestión judicial", "oralidad",
            
            # Rural and PDET context
            "privados de libertad de zonas rurales", "campesinos recluidos",
            "delitos relacionados con cultivos ilícitos", "pequeños cultivadores",
            "criminalización de la pobreza", "dosis mínima",
            "personas privadas por delitos menores",
            
            # Conflict-related imprisonment
            "excombatientes privados de libertad", "presos políticos",
            "delitos políticos", "conexidad", "amnistía", "indulto",
            "privados de libertad por el conflicto",
            
            # Family and social connections
            "visitas familiares", "visita íntima", "comunicación familiar",
            "distancia de las cárceles", "traslados", "cercanía familiar",
            "impacto en familias rurales", "costos de visita",
            
            # Infrastructure problems
            "infraestructura carcelaria", "deterioro de instalaciones",
            "construcción de cárceles", "ampliación de cupos",
            "espacios inadecuados", "celdas", "calabozos",
            
            # PDET-specific
            "acceso a justicia en zonas rurales", "defensores públicos",
            "casas de justicia", "consultorios jurídicos",
            
            # Institutions
            "Defensoría del Pueblo", "Procuraduría", "Corte Constitucional",
            "INPEC", "Ministerio de Justicia", "Fiscalía",
            "jueces de ejecución de penas", "defensoría pública"
        ]
    },
    
    "PA10": {
        "name": "Migración transfronteriza",
        "legacy": "P10",
        "pdet_focus": "Migración venezolana en zonas de frontera, integración rural y desafíos humanitarios",
        "keywords": [
            # Migration - General
            "migración", "migrante", "migrantes", "migración transfronteriza",
            "flujos migratorios", "movilidad humana", "migración internacional",
            "migración irregular", "migración pendular", "caminantes",
            "tránsito migratorio", "rutas migratorias",
            
            # Refugees and asylum
            "refugiado", "refugiados", "solicitantes de asilo", "protección internacional",
            "estatuto de refugiado", "reconocimiento de refugiado",
            "necesidad de protección", "persecución",
            
            # Venezuelan migration - Dominant flow
            "migración venezolana", "venezolanos", "éxodo venezolano",
            "crisis venezolana", "diáspora venezolana",
            "familias venezolanas", "población venezolana",
            "refugiados venezolanos", "migrantes económicos",
            
            # Border - Regional context
            "frontera", "zona de frontera", "paso fronterizo", "control migratorio",
            "frontera colombo-venezolana", "frontera norte", "frontera sur",
            "La Guajira", "Norte de Santander", "Arauca", "Vichada", "Guainía",
            "Cúcuta", "Maicao", "Paraguachón", "Arauca ciudad",
            "pasos irregulares", "trochas", "cruces informales",
            "cierre de frontera", "reapertura de frontera",
            
            # Regularization - Documentation
            "regularización", "documentación", "permisos", "PPT", "Permiso de Permanencia",
            "PEP", "Permiso Especial de Permanencia", "TMF", "Tarjeta de Movilidad Fronteriza",
            "PPT-E", "Permiso por Protección Temporal", "Estatuto Temporal",
            "registro biométrico", "cédula de extranjería",
            "documentos de identidad", "pasaportes", "certificados",
            "caracterización migratoria", "RAMV", "Registro Administrativo",
            
            # Integration - Social and economic
            "integración", "inclusión social", "acceso a servicios", "derechos de migrantes",
            "integración socioeconómica", "integración laboral",
            "empleabilidad de migrantes", "trabajo informal",
            "explotación laboral", "precarización laboral",
            "emprendimiento migrante", "medios de vida",
            "convivencia ciudadana", "cohesión social",
            "discriminación", "xenofobia", "rechazo social",
            
            # Access to services - Critical needs
            "salud para migrantes", "atención en salud", "vacunación",
            "salud materno-infantil", "desnutrición infantil migrante",
            "educación para migrantes", "acceso escolar", "validación de estudios",
            "convalidación de títulos", "niños migrantes en escuelas",
            "vivienda para migrantes", "alojamiento temporal",
            "saneamiento básico", "condiciones habitacionales",
            
            # Humanitarian - Emergency response
            "crisis humanitaria", "asistencia humanitaria", "albergues", "atención humanitaria",
            "ayuda humanitaria", "emergencia humanitaria",
            "puntos de atención", "PAAMS", "Puestos de Atención",
            "kits humanitarios", "alimentación", "agua potable",
            "atención de emergencia", "primeros auxilios",
            "protección en tránsito", "riesgos en ruta",
            
            # Vulnerable populations
            "mujeres migrantes", "niños migrantes", "familias migrantes",
            "migrantes LGBTI", "adultos mayores migrantes",
            "personas con discapacidad migrantes",
            "mujeres gestantes migrantes", "partos de migrantes",
            "niñez migrante", "adolescentes migrantes",
            "menores no acompañados", "separación familiar",
            
            # Protection risks
            "trata de personas", "tráfico de migrantes", "explotación sexual",
            "reclutamiento forzado de migrantes", "violencia basada en género",
            "extorsión a migrantes", "criminalidad contra migrantes",
            "redes de tráfico", "rutas de trata",
            
            # Rural and PDET context
            "migración en zonas rurales", "migrantes en áreas rurales",
            "trabajo agrícola migrante", "jornaleros migrantes",
            "mano de obra rural", "agricultura y migración",
            "asentamientos informales rurales", "ocupación de baldíos",
            "frontera agrícola y migración",
            
            # Economic impact
            "impacto económico de la migración", "mercado laboral",
            "competencia laboral", "informalidad",
            "remesas", "economía local", "comercio fronterizo",
            "servicios públicos", "presión sobre servicios",
            
            # Social cohesion
            "convivencia", "tejido social", "conflictos sociales",
            "competencia por recursos", "tensiones comunitarias",
            "mediación comunitaria", "diálogo intercultural",
            
            # Mixed migration
            "flujos mixtos", "otras nacionalidades", "migración haitiana",
            "migración cubana", "tránsito hacia otros países",
            "migración extracontinental", "migración africana",
            "migración asiática", "Darién", "ruta del Pacífico",
            
            # Return and circulation
            "retorno voluntario", "retorno asistido", "deportaciones",
            "migración circular", "ida y vuelta", "retornados colombianos",
            "colombianos en el exterior", "diáspora colombiana",
            
            # Legal framework
            "normatividad migratoria", "Ley de Migración", "decretos",
            "resoluciones migratorias", "marco legal",
            "derechos de los migrantes", "principio de no devolución",
            "debido proceso migratorio",
            
            # Institutional coordination
            "coordinación interinstitucional", "Grupo de Migración",
            "GIFMM", "Grupo Interagencial sobre Flujos Migratorios Mixtos",
            "mesas de trabajo", "comités territoriales",
            "articulación nacional-territorial",
            
            # Data and monitoring
            "información migratoria", "caracterización", "censos",
            "monitoreo de flujos", "estadísticas migratorias",
            "sistemas de información", "datos desagregados",
            
            # PDET-specific
            "migración en municipios PDET", "frontera y PDET",
            "integración en territorios rurales",
            "impacto en construcción de paz",
            
            # Institutions
            "Migración Colombia", "ACNUR", "Alto Comisionado de las Naciones Unidas para los Refugiados",
            "OIM", "Organización Internacional para las Migraciones",
            "UNICEF", "OPS/OMS", "PMA", "Programa Mundial de Alimentos",
            "Cancillería", "Ministerio de Relaciones Exteriores",
            "Gerencia de Frontera", "GIFMM local",
            "Cruz Roja", "organizaciones humanitarias", "ONG migratorias"
        ]
    }
}
