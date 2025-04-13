% --- HECHOS DINÁMICOS ---
:- dynamic piel/2.
:- dynamic piel_sensible/1.
:- dynamic preferencia_marca/2.
:- dynamic preferencia_tipo_base/2.
:- dynamic feedback/3.
:- dynamic disponible/1.
:- dynamic alergia/2.

% Ingredientes irritantes
ingrediente_irritante(alcohol_denat).
ingrediente_irritante(propilenglicol).
ingrediente_irritante(parabenos).
ingrediente_irritante(fragancia_sintetica).
ingrediente_irritante(octinoxato).
ingrediente_irritante(benzofenona).
ingrediente_irritante(formaldehido).

% Ingredientes comedogénicos
ingrediente_comedogenico(siliconas).
ingrediente_comedogenico(aceite_mineral).
ingrediente_comedogenico(acido_estearico).
ingrediente_comedogenico(manteca_de_cacao).

% Ingredientes beneficiosos
ingrediente_benefico(dioxido_de_titanio).
ingrediente_benefico(oxido_de_zinc).
ingrediente_benefico(bisabolol).
ingrediente_benefico(vitamina_e).
ingrediente_benefico(aloe_vera).
ingrediente_benefico(niacinamida).
ingrediente_benefico(acido_hialuronico).

% Clasificación de marcas por gama
gama_marca(maybelline, media).
gama_marca(loreal, media).
gama_marca(mac, alta).
gama_marca(dior, alta).
gama_marca(essence, baja).
gama_marca(jordana, baja).
gama_marca(estee_lauder, alta).
gama_marca(catrice, media).
gama_marca(bobbi_brown, alta).
gama_marca(shiseido, alta).
gama_marca(bourjois, media).
gama_marca(wet_n_wild, media).
gama_marca(stila, media).

% Base(nombre, tipo, marca, ingredientes)
base("Fit Me Matte", liquida, maybelline, [dioxido_de_titanio, oxido_de_zinc]).
base("SuperStay Full Coverage", liquida, maybelline, [alcohol_denat, siliconas]).
base("True Match", liquida, loreal, [vitamina_e, propilenglicol]).
base("Double Wear", liquida, estee_lauder, [oxido_de_zinc, fragancia_sintetica]).
base("Studio Fix Powder", en_polvo, mac, [dioxido_de_titanio, siliconas]).
base("Nude Illusion", liquida, catrice, [aloe_vera, parabenos]).
base("Fresh & Fit", liquida, essence, [alcohol_denat]).
base("Dream Matte Mousse", crema, maybelline, [oxido_de_zinc, acido_estearico]).
base("Skin Long-Wear Weightless", liquida, bobbi_brown, [niacinamida, oxido_de_zinc, acido_hialuronico]).
base("Forever Skin Glow", liquida, dior, [aloe_vera, vitamina_e, dioxido_de_titanio]).
base("Synchro Skin Radiant Lifting", liquida, shiseido, [acido_hialuronico, oxido_de_zinc, bisabolol]).
base("Healthy Mix", liquida, bourjois, [vitamina_e, niacinamida, aloe_vera]).
base("Photofocus Foundation", liquida, wet_n_wild, [dioxido_de_titanio, oxido_de_zinc]).
base("Stay All Day", liquida, stila, [oxido_de_zinc, acido_hialuronico]).
base("HD Liquid Coverage", liquida, catrice, [niacinamida, oxido_de_zinc]).
base("Soft Touch Mousse", crema, essence, [vitamina_e, bisabolol]).
base("Even Skin Tone", liquida, jordana, [dioxido_de_titanio, aloe_vera]).
base("Mineralize Loose", en_polvo, mac, [oxido_de_zinc, bisabolol]).
base("Blur Stick", barra, loreal, [dioxido_de_titanio, niacinamida]).

% --- REGLAS ---
recomendar_base(Usuario, Base) :-
    piel(Usuario, _),
    preferencia_marca(Usuario, Gama),
    preferencia_tipo_base(Usuario, TipoBase),
    (   piel_sensible(Usuario) ->
        base(Base, TipoBase, Marca, Ingredientes),
        gama_marca(Marca, Gama),
        not((member(Irr, Ingredientes), ingrediente_irritante(Irr))),
        not((member(Com, Ingredientes), ingrediente_comedogenico(Com))),
        not((alergia(Usuario, A), member(A, Ingredientes))),
        tiene_ingrediente_benefico(Ingredientes),
        disponible(Base)
    ;
        base(Base, TipoBase, Marca, Ingredientes),
        gama_marca(Marca, Gama),
        not((member(Com, Ingredientes), ingrediente_comedogenico(Com))),
        not((alergia(Usuario, A), member(A, Ingredientes))),
        disponible(Base)
    ).

recomendar_base_cercana(Usuario, Base) :-
    piel(Usuario, _),  % antes: piel(Usuario, TipoPiel),
    preferencia_marca(Usuario, Gama),
    preferencia_tipo_base(Usuario, TipoBase),
    base(Base, TipoBase, Marca, _),
    gama_marca(Marca, Gama),
    disponible(Base).

% Reglas específicas por tipo de piel
base_para_piel_grasa(Base) :-
    base(Base, _, _, Ingredientes),
    not(member(aceite_mineral, Ingredientes)),
    not(member(siliconas, Ingredientes)).

base_para_piel_seca(Base) :-
    base(Base, _, _, Ingredientes),
    member(aloe_vera, Ingredientes).

base_para_piel_sensible(Base) :-
    base(Base, _, _, Ingredientes),
    not((member(Irr, Ingredientes), ingrediente_irritante(Irr))).

% Regla para alergias
evitar_alergia(Base, Usuario) :-
    alergia(Usuario, Alergeno),
    base(Base, _, _, Ingredientes),
    member(Alergeno, Ingredientes).

% Registro de usuario y preferencias
registrar_usuario(Nombre, TipoPiel, Sensible, Gama, TipoBase) :-
    assertz(piel(Nombre, TipoPiel)),
    (Sensible == si -> assertz(piel_sensible(Nombre)); true),
    assertz(preferencia_marca(Nombre, Gama)),
    assertz(preferencia_tipo_base(Nombre, TipoBase)).

% Asegurarse de que la base está disponible
agregar_disponibilidad(Base) :-
    assertz(disponible(Base)).

% Agregar alergias
agregar_alergia(Usuario, Ingrediente) :-
    assertz(alergia(Usuario, Ingrediente)).

% Interfaz de línea (opcional)
iniciar :-
    write('Bienvenido al sistema experto de recomendaciones de bases.\n'),
    write('Ingrese su nombre: '), read(Nombre),
    write('Tipo de piel (grasa, seca, mixta, normal): '), read(TipoPiel),
    write('Tiene piel sensible? (si/no): '), read(Sensible),
    write('Gama preferida (alta, media, baja): '), read(Gama),
    write('Tipo de base preferido (liquida, en_polvo, crema, barra, polvo_compacto): '), read(TipoBase),
    registrar_usuario(Nombre, TipoPiel, Sensible, Gama, TipoBase),
    write('¿Tiene alguna alergia a algún ingrediente? (si/no): '), read(Alergia),
    (Alergia == si ->
        write('Ingrese el ingrediente al que es alérgico: '), read(Ingrediente),
        agregar_alergia(Nombre, Ingrediente)
    ; true),
    recomendar_bases(Nombre).

recomendar_bases(Nombre) :-
    (   recomendar_base(Nombre, Base) ->
        write('Bases recomendadas para usted:\n'),
        write(Base), nl
    ;   recomendar_base_cercana(Nombre, Base) ->
        write('No hay bases exactas, pero la más cercana es:\n'),
        write(Base), nl
    ;   write('Lo sentimos, no tenemos bases recomendadas para su perfil.\n')
    ).

% Bases disponibles por defecto
:- agregar_disponibilidad("Fit Me Matte").
:- agregar_disponibilidad("SuperStay Full Coverage").
:- agregar_disponibilidad("True Match").
:- agregar_disponibilidad("Double Wear").
:- agregar_disponibilidad("Studio Fix Powder").
:- agregar_disponibilidad("Nude Illusion").
:- agregar_disponibilidad("Fresh & Fit").
:- agregar_disponibilidad("Dream Matte Mousse").
:- agregar_disponibilidad("Skin Long-Wear Weightless").
:- agregar_disponibilidad("Forever Skin Glow").
:- agregar_disponibilidad("Synchro Skin Radiant Lifting").
:- agregar_disponibilidad("Healthy Mix").
:- agregar_disponibilidad("Photofocus Foundation").
:- agregar_disponibilidad("Stay All Day").
:- agregar_disponibilidad("HD Liquid Coverage").
:- agregar_disponibilidad("Soft Touch Mousse").
:- agregar_disponibilidad("Even Skin Tone").
:- agregar_disponibilidad("Mineralize Loose").
:- agregar_disponibilidad("Blur Stick").