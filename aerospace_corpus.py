# AeroScientia — Corpus de Entrenamiento
# Textos técnicos reales de dominio aeroespacial (NASA, FAA, AIAA style)
# Fuente: Adaptaciones de documentos públicos NASA NTRS, FAA Handbooks

CORPUS_TEXTS = [
    # ── AERONAUTICS ──────────────────────────────────────────────────────
    {
        "id": "aero_001",
        "domain": "aeronautics",
        "source": "FAA Pilot's Handbook of Aeronautical Knowledge",
        "lang": "en",
        "text": """
        The lift equation L = (1/2) * rho * v^2 * S * CL demonstrates that lift is 
        proportional to air density (rho), the square of velocity (v), wing area (S), 
        and the lift coefficient (CL). The angle of attack directly influences the lift 
        coefficient; as the angle of attack increases, CL increases until the critical 
        angle is reached, beyond which airflow separation causes a stall condition.
        Bernoulli's principle states that as airspeed increases over the airfoil's upper 
        surface (extrados), static pressure decreases, creating a pressure differential 
        that generates the upward aerodynamic force known as lift. The Navier-Stokes 
        equations govern the viscous flow behavior across the entire wing surface.
        Parasitic drag (CD_parasitic) increases with the square of velocity, while 
        induced drag (CD_induced) decreases with velocity squared. The drag polar 
        equation CD = CD0 + (CL^2 / pi * e * AR) relates total drag to lift via the 
        Oswald efficiency factor (e) and aspect ratio (AR).
        """,
        "entities": [
            ("lift equation", "EQUATION"),
            ("L = (1/2) * rho * v^2 * S * CL", "EQUATION"),
            ("air density", "PHYSICAL_CONSTANT"),
            ("rho", "PHYSICAL_CONSTANT"),
            ("velocity", "PARAMETER"),
            ("wing area", "PARAMETER"),
            ("lift coefficient", "PARAMETER"),
            ("CL", "PARAMETER"),
            ("angle of attack", "PARAMETER"),
            ("stall condition", "FLIGHT_PHENOMENON"),
            ("Bernoulli's principle", "PHYSICAL_LAW"),
            ("airfoil", "COMPONENT"),
            ("extrados", "COMPONENT"),
            ("static pressure", "PHYSICAL_CONSTANT"),
            ("lift", "FORCE"),
            ("Navier-Stokes equations", "EQUATION"),
            ("viscous flow", "FLUID_CONCEPT"),
            ("Parasitic drag", "FORCE"),
            ("CD_parasitic", "PARAMETER"),
            ("induced drag", "FORCE"),
            ("CD_induced", "PARAMETER"),
            ("drag polar equation", "EQUATION"),
            ("Oswald efficiency factor", "PARAMETER"),
            ("aspect ratio", "PARAMETER"),
            ("AR", "PARAMETER"),
        ]
    },
    {
        "id": "aero_002",
        "domain": "aeronautics",
        "source": "AIAA Journal of Aircraft",
        "lang": "en",
        "text": """
        The turbofan engine cycle operates on the Brayton thermodynamic cycle, wherein 
        ambient air is compressed by the compressor stage, mixed with fuel in the 
        combustion chamber, and expanded through the turbine and nozzle to generate 
        thrust according to Newton's Third Law of Motion. The bypass ratio (BPR) 
        determines the proportion of total airflow that bypasses the core engine; 
        modern high-bypass turbofan engines (BPR > 8) achieve specific fuel consumption 
        (SFC) values below 0.53 lb/lbf/hr. The overall pressure ratio (OPR) in 
        advanced engines exceeds 50:1, increasing thermal efficiency significantly.
        The compressor pressure ratio stages utilize NACA airfoil profiles to maximize 
        isentropic efficiency. Reynolds number (Re = rho * v * L / mu) governs the 
        boundary layer transition from laminar to turbulent flow on the compressor blades.
        Mach number (Ma = v / a) is critical in transonic compressor design where 
        shock-induced separation must be controlled through advanced blade sweep angles.
        """,
        "entities": [
            ("turbofan engine", "VEHICLE_TYPE"),
            ("Brayton thermodynamic cycle", "PHYSICAL_LAW"),
            ("compressor stage", "COMPONENT"),
            ("combustion chamber", "COMPONENT"),
            ("turbine", "COMPONENT"),
            ("nozzle", "COMPONENT"),
            ("thrust", "FORCE"),
            ("Newton's Third Law of Motion", "PHYSICAL_LAW"),
            ("bypass ratio", "PARAMETER"),
            ("BPR", "PARAMETER"),
            ("high-bypass turbofan engines", "VEHICLE_TYPE"),
            ("specific fuel consumption", "PARAMETER"),
            ("SFC", "PARAMETER"),
            ("overall pressure ratio", "PARAMETER"),
            ("OPR", "PARAMETER"),
            ("thermal efficiency", "PARAMETER"),
            ("NACA airfoil profiles", "COMPONENT"),
            ("isentropic efficiency", "PARAMETER"),
            ("Reynolds number", "PHYSICAL_CONSTANT"),
            ("Re = rho * v * L / mu", "EQUATION"),
            ("boundary layer", "FLUID_CONCEPT"),
            ("laminar", "FLUID_CONCEPT"),
            ("turbulent flow", "FLUID_CONCEPT"),
            ("Mach number", "PARAMETER"),
            ("Ma = v / a", "EQUATION"),
            ("transonic", "FLIGHT_REGIME"),
            ("shock-induced separation", "FLIGHT_PHENOMENON"),
        ]
    },
    {
        "id": "aero_003",
        "domain": "aeronautics",
        "source": "NASA Technical Memorandum",
        "lang": "en",
        "text": """
        Computational Fluid Dynamics (CFD) simulations using Reynolds-Averaged 
        Navier-Stokes (RANS) equations with k-omega SST turbulence model were 
        conducted to evaluate the aerodynamic performance of the supercritical wing 
        design. The wing features a modified NACA 64A-series airfoil with a thickness-
        to-chord ratio (t/c) of 0.12 and a leading edge sweep angle of 35 degrees.
        Pitching moment coefficient (Cm) stability requirements mandate a negative 
        Cm slope (dCm/dCL < 0) for inherent longitudinal stability. The aerodynamic 
        center is located at approximately 25% of the mean aerodynamic chord (MAC) for 
        subsonic configurations. Wing loading (W/S) for the reference aircraft is 
        620 N/m^2, consistent with medium-range commercial transport category.
        The fuselage cross-section drag coefficient (CD_fuse) was minimized through 
        area-ruling (Whitcomb area rule) to reduce wave drag in the transonic regime.
        """,
        "entities": [
            ("Computational Fluid Dynamics", "METHODOLOGY"),
            ("CFD", "METHODOLOGY"),
            ("Reynolds-Averaged Navier-Stokes", "EQUATION"),
            ("RANS", "EQUATION"),
            ("k-omega SST turbulence model", "METHODOLOGY"),
            ("supercritical wing", "COMPONENT"),
            ("NACA 64A-series airfoil", "COMPONENT"),
            ("thickness-to-chord ratio", "PARAMETER"),
            ("t/c", "PARAMETER"),
            ("leading edge sweep angle", "PARAMETER"),
            ("Pitching moment coefficient", "PARAMETER"),
            ("Cm", "PARAMETER"),
            ("longitudinal stability", "FLIGHT_PHENOMENON"),
            ("aerodynamic center", "PARAMETER"),
            ("mean aerodynamic chord", "PARAMETER"),
            ("MAC", "PARAMETER"),
            ("Wing loading", "PARAMETER"),
            ("W/S", "PARAMETER"),
            ("fuselage", "COMPONENT"),
            ("Whitcomb area rule", "PHYSICAL_LAW"),
            ("wave drag", "FORCE"),
            ("transonic regime", "FLIGHT_REGIME"),
        ]
    },

    # ── ASTRODYNAMICS ─────────────────────────────────────────────────────
    {
        "id": "astro_001",
        "domain": "astrodynamics",
        "source": "NASA Mission Design Handbook",
        "lang": "en",
        "text": """
        The Tsiolkovsky rocket equation (Delta-v = ve * ln(m0/mf)) governs all 
        propulsive maneuvers in the vacuum of space. The specific impulse (Isp) 
        quantifies propellant efficiency; chemical rockets achieve Isp values of 
        250-450 seconds, while ion thrusters achieve 1,500-10,000 seconds at the 
        cost of very low thrust levels. The mass ratio (m0/mf) determines achievable 
        Delta-v for a given Isp via the rocket equation.
        Orbital mechanics follows Kepler's laws of planetary motion. The vis-viva 
        equation (v^2 = GM * (2/r - 1/a)) relates orbital velocity to the 
        semi-major axis (a) and current orbital radius (r). Newton's law of 
        universal gravitation (F = G * m1 * m2 / r^2) provides the fundamental 
        attractive force that maintains orbital trajectories.
        A Hohmann transfer orbit is the minimum-energy elliptical path between two 
        circular orbits, requiring two Delta-v burns. The first burn raises the 
        apoapsis to the target orbit altitude; the second circularizes at apoapsis.
        """,
        "entities": [
            ("Tsiolkovsky rocket equation", "EQUATION"),
            ("Delta-v = ve * ln(m0/mf)", "EQUATION"),
            ("Delta-v", "PARAMETER"),
            ("specific impulse", "PARAMETER"),
            ("Isp", "PARAMETER"),
            ("chemical rockets", "VEHICLE_TYPE"),
            ("ion thrusters", "COMPONENT"),
            ("mass ratio", "PARAMETER"),
            ("m0/mf", "PARAMETER"),
            ("Orbital mechanics", "METHODOLOGY"),
            ("Kepler's laws of planetary motion", "PHYSICAL_LAW"),
            ("vis-viva equation", "EQUATION"),
            ("v^2 = GM * (2/r - 1/a)", "EQUATION"),
            ("orbital velocity", "PARAMETER"),
            ("semi-major axis", "PARAMETER"),
            ("orbital radius", "PARAMETER"),
            ("Newton's law of universal gravitation", "PHYSICAL_LAW"),
            ("F = G * m1 * m2 / r^2", "EQUATION"),
            ("orbital trajectories", "FLIGHT_PHENOMENON"),
            ("Hohmann transfer orbit", "MANEUVER"),
            ("apoapsis", "ORBITAL_ELEMENT"),
            ("Delta-v burns", "MANEUVER"),
        ]
    },
    {
        "id": "astro_002",
        "domain": "astrodynamics",
        "source": "ESA Mission Analysis Guidelines",
        "lang": "en",
        "text": """
        Orbital elements (Keplerian elements) fully describe a spacecraft's trajectory: 
        semi-major axis (a), eccentricity (e), inclination (i), right ascension of the 
        ascending node (RAAN or Omega), argument of periapsis (omega), and true anomaly 
        (nu). Low Earth Orbit (LEO) ranges from 160 to 2,000 km altitude with orbital 
        periods of approximately 90-127 minutes. Geostationary orbit (GEO) at 35,786 km 
        altitude has an orbital period matching Earth's rotation (23h 56m 4s).
        The Reaction Control System (RCS) uses small hydrazine thrusters for attitude 
        control and fine orbital adjustments. Attitude Determination and Control System 
        (ADCS) maintains spacecraft orientation using star trackers, gyroscopes, and 
        reaction wheels. Gravitational perturbations from the Earth's oblateness (J2 
        coefficient) cause secular drift in RAAN of approximately -6.97 deg/day for ISS.
        Thermal control in vacuum relies entirely on radiation (Stefan-Boltzmann law: 
        P = sigma * A * T^4) since conduction and convection are absent.
        """,
        "entities": [
            ("Orbital elements", "METHODOLOGY"),
            ("Keplerian elements", "METHODOLOGY"),
            ("semi-major axis", "ORBITAL_ELEMENT"),
            ("eccentricity", "ORBITAL_ELEMENT"),
            ("inclination", "ORBITAL_ELEMENT"),
            ("right ascension of the ascending node", "ORBITAL_ELEMENT"),
            ("RAAN", "ORBITAL_ELEMENT"),
            ("argument of periapsis", "ORBITAL_ELEMENT"),
            ("true anomaly", "ORBITAL_ELEMENT"),
            ("Low Earth Orbit", "ORBIT_TYPE"),
            ("LEO", "ORBIT_TYPE"),
            ("Geostationary orbit", "ORBIT_TYPE"),
            ("GEO", "ORBIT_TYPE"),
            ("Reaction Control System", "COMPONENT"),
            ("RCS", "COMPONENT"),
            ("hydrazine thrusters", "COMPONENT"),
            ("Attitude Determination and Control System", "COMPONENT"),
            ("ADCS", "COMPONENT"),
            ("star trackers", "COMPONENT"),
            ("reaction wheels", "COMPONENT"),
            ("J2 coefficient", "PHYSICAL_CONSTANT"),
            ("Stefan-Boltzmann law", "PHYSICAL_LAW"),
            ("P = sigma * A * T^4", "EQUATION"),
        ]
    },
    {
        "id": "astro_003",
        "domain": "astrodynamics",
        "source": "NASA JPL Interplanetary Mission Design",
        "lang": "en",
        "text": """
        Interplanetary trajectories exploit the patched conic approximation, dividing 
        the mission into three phases: departure hyperbola from Earth, heliocentric 
        transfer ellipse, and arrival hyperbola at the target planet. The hyperbolic 
        excess velocity (v_infinity) determines the energy required for escape from 
        Earth's sphere of influence (SOI). For a Mars transfer via Hohmann orbit, 
        the required C3 (characteristic energy = v_infinity^2) is approximately 
        8.7 km^2/s^2. Planetary gravity assists (flyby maneuvers) can augment 
        spacecraft velocity without propellant expenditure, leveraging the planet's 
        gravitational potential energy via the Oberth effect.
        Aerobraking utilizes atmospheric drag to reduce orbital energy during planetary 
        orbit insertion, significantly reducing propellant mass fraction requirements. 
        Entry, Descent, and Landing (EDL) sequences must manage thermal loads from 
        aerodynamic heating (Q = 1/2 * rho * v^3 * CD * A) with ablative heat shields.
        """,
        "entities": [
            ("patched conic approximation", "METHODOLOGY"),
            ("departure hyperbola", "ORBIT_TYPE"),
            ("heliocentric transfer ellipse", "ORBIT_TYPE"),
            ("arrival hyperbola", "ORBIT_TYPE"),
            ("hyperbolic excess velocity", "PARAMETER"),
            ("v_infinity", "PARAMETER"),
            ("sphere of influence", "PARAMETER"),
            ("SOI", "PARAMETER"),
            ("C3", "PARAMETER"),
            ("characteristic energy", "PARAMETER"),
            ("v_infinity^2", "EQUATION"),
            ("gravity assists", "MANEUVER"),
            ("flyby maneuvers", "MANEUVER"),
            ("Oberth effect", "PHYSICAL_LAW"),
            ("Aerobraking", "MANEUVER"),
            ("Entry, Descent, and Landing", "MANEUVER"),
            ("EDL", "MANEUVER"),
            ("aerodynamic heating", "FLIGHT_PHENOMENON"),
            ("Q = 1/2 * rho * v^3 * CD * A", "EQUATION"),
            ("ablative heat shields", "COMPONENT"),
        ]
    },

    # ── PROPULSION ────────────────────────────────────────────────────────
    {
        "id": "prop_001",
        "domain": "propulsion",
        "source": "NASA Propulsion Research Center Report",
        "lang": "en",
        "text": """
        Hall-effect thrusters (HET) ionize propellant (typically xenon) using electron 
        bombardment and accelerate ions via crossed electric and magnetic fields, 
        achieving exhaust velocities of 15-30 km/s compared to 2.9-4.5 km/s for 
        chemical bipropellant systems. The thrust equation for electric propulsion 
        is T = m_dot * ve + (Pe - Pa) * Ae, where m_dot is mass flow rate, ve is 
        exhaust velocity, Pe is exit pressure, Pa is ambient pressure, and Ae is 
        nozzle exit area. The figure of merit for propulsion systems is the 
        propellant mass fraction (PMF = mp / m0).
        Nuclear thermal propulsion (NTP) uses a fission reactor to heat hydrogen 
        propellant to extreme temperatures before expansion through a nozzle, 
        achieving Isp of 800-1000 seconds. The NERVA program demonstrated NTP 
        feasibility in the 1960s. For solar electric propulsion (SEP), the power-
        to-thrust ratio (P/T) and solar array specific power (W/kg) are primary 
        design drivers.
        """,
        "entities": [
            ("Hall-effect thrusters", "COMPONENT"),
            ("HET", "COMPONENT"),
            ("xenon", "PHYSICAL_CONSTANT"),
            ("exhaust velocities", "PARAMETER"),
            ("chemical bipropellant systems", "COMPONENT"),
            ("thrust equation", "EQUATION"),
            ("T = m_dot * ve + (Pe - Pa) * Ae", "EQUATION"),
            ("mass flow rate", "PARAMETER"),
            ("m_dot", "PARAMETER"),
            ("exhaust velocity", "PARAMETER"),
            ("nozzle exit area", "PARAMETER"),
            ("Ae", "PARAMETER"),
            ("propellant mass fraction", "PARAMETER"),
            ("PMF", "PARAMETER"),
            ("Nuclear thermal propulsion", "COMPONENT"),
            ("NTP", "COMPONENT"),
            ("fission reactor", "COMPONENT"),
            ("Isp", "PARAMETER"),
            ("NERVA program", "PHYSICAL_LAW"),
            ("solar electric propulsion", "COMPONENT"),
            ("SEP", "COMPONENT"),
            ("power-to-thrust ratio", "PARAMETER"),
            ("P/T", "PARAMETER"),
        ]
    },

    # ── MATERIALS ─────────────────────────────────────────────────────────
    {
        "id": "mat_001",
        "domain": "materials",
        "source": "AIAA Structures, Structural Dynamics and Materials",
        "lang": "en",
        "text": """
        Carbon fiber reinforced polymer (CFRP) composites achieve specific stiffness 
        values (E/rho) up to 5x those of aluminum 7075-T6 alloy while reducing 
        structural mass by 20-30%. The Boeing 787 Dreamliner fuselage consists of 
        approximately 50% CFRP by weight. Fatigue crack propagation in aerospace 
        alloys is governed by the Paris law: da/dN = C * (Delta-K)^m, where 
        Delta-K is the stress intensity factor range, and C and m are material 
        constants. Titanium alloy Ti-6Al-4V offers an excellent strength-to-weight 
        ratio (sigma_ult/rho = 250 kN*m/kg) with superior corrosion resistance.
        Thermal protection systems (TPS) for reentry vehicles utilize ablative 
        materials (PICA - Phenolic Impregnated Carbon Ablator) or ceramic tiles 
        (HRSI - High-temperature Reusable Surface Insulation) to withstand 
        stagnation temperatures exceeding 1650°C during atmospheric entry.
        """,
        "entities": [
            ("Carbon fiber reinforced polymer", "MATERIAL"),
            ("CFRP", "MATERIAL"),
            ("specific stiffness", "PARAMETER"),
            ("E/rho", "PARAMETER"),
            ("aluminum 7075-T6 alloy", "MATERIAL"),
            ("Boeing 787 Dreamliner", "VEHICLE_TYPE"),
            ("Paris law", "PHYSICAL_LAW"),
            ("da/dN = C * (Delta-K)^m", "EQUATION"),
            ("stress intensity factor", "PARAMETER"),
            ("Delta-K", "PARAMETER"),
            ("Titanium alloy Ti-6Al-4V", "MATERIAL"),
            ("strength-to-weight ratio", "PARAMETER"),
            ("sigma_ult/rho", "PARAMETER"),
            ("Thermal protection systems", "COMPONENT"),
            ("TPS", "COMPONENT"),
            ("ablative materials", "MATERIAL"),
            ("PICA", "MATERIAL"),
            ("Phenolic Impregnated Carbon Ablator", "MATERIAL"),
            ("ceramic tiles", "MATERIAL"),
            ("HRSI", "MATERIAL"),
            ("stagnation temperatures", "PARAMETER"),
            ("atmospheric entry", "FLIGHT_PHENOMENON"),
        ]
    },
]

# ── ESPAÑOL — Muestra de textos técnicos en español ───────────────────────
CORPUS_ES = [
    {
        "id": "aero_es_001",
        "domain": "aeronautics",
        "source": "Manual de Piloto FAA — Traducción Oficial",
        "lang": "es",
        "text": """
        La ecuación de sustentación L = (1/2) * rho * v^2 * S * CL demuestra que la 
        fuerza ascendente es proporcional a la densidad del aire (rho), el cuadrado de 
        la velocidad relativa (v), la superficie alar (S) y el coeficiente de 
        sustentación (CL). El ángulo de ataque influye directamente en el coeficiente 
        de sustentación; al aumentar el ángulo de ataque, el CL incrementa hasta el 
        ángulo crítico, más allá del cual la separación del flujo causa una entrada en 
        pérdida (pérdida aerodinámica o stall). El principio de Bernoulli establece 
        que al aumentar la velocidad del flujo sobre el extradós del perfil alar, 
        disminuye la presión estática, creando el diferencial de presión que genera 
        la fuerza ascendente. Las ecuaciones de Navier-Stokes gobiernan el comportamiento 
        del flujo viscoso sobre toda la superficie del ala.
        """,
        "entities": [
            ("ecuación de sustentación", "EQUATION"),
            ("densidad del aire", "PHYSICAL_CONSTANT"),
            ("velocidad relativa", "PARAMETER"),
            ("superficie alar", "PARAMETER"),
            ("coeficiente de sustentación", "PARAMETER"),
            ("ángulo de ataque", "PARAMETER"),
            ("entrada en pérdida", "FLIGHT_PHENOMENON"),
            ("pérdida aerodinámica", "FLIGHT_PHENOMENON"),
            ("stall", "FLIGHT_PHENOMENON"),
            ("principio de Bernoulli", "PHYSICAL_LAW"),
            ("extradós", "COMPONENT"),
            ("perfil alar", "COMPONENT"),
            ("presión estática", "PHYSICAL_CONSTANT"),
            ("fuerza ascendente", "FORCE"),
            ("ecuaciones de Navier-Stokes", "EQUATION"),
            ("flujo viscoso", "FLUID_CONCEPT"),
        ]
    },
]
