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

% Base(nombre, tipo, marca, ingredientes)
base("Fit Me Matte", liquida, maybelline, [dioxido_de_titanio, oxido_de_zinc]).
base("SuperStay Full Coverage", liquida, maybelline, [alcohol_denat, siliconas]).
base("True Match", liquida, loreal, [vitamina_e, propilenglicol]).
base("Double Wear", liquida, estee_lauder, [oxido_de_zinc, fragancia_sintetica]).
base("Studio Fix Powder", en_polvo, mac, [dioxido_de_titanio, siliconas]).
base("Nude Illusion", liquida, catrice, [aloe_vera, parabenos]).
base("Fresh & Fit", liquida, essence, [alcohol_denat]).
base("Dream Matte Mousse", crema, maybelline, [oxido_de_zinc, acido_estearico]).

% --- REGLAS ---
recomendar_base(Usuario, Base) :-
    piel(Usuario, _),  % antes: piel(Usuario, TipoPiel),
    preferencia_marca(Usuario, Gama),
    preferencia_tipo_base(Usuario, TipoBase),
    (   piel_sensible(Usuario) ->
        base(Base, TipoBase, Marca, Ingredientes),
        gama_marca(Marca, Gama),
        not((member(Irr, Ingredientes), ingrediente_irritante(Irr))),
        not((member(Com, Ingredientes), ingrediente_comedogenico(Com))),
        member(Benef, Ingredientes), ingrediente_benefico(Benef),
        disponible(Base)
    ;
        base(Base, TipoBase, Marca, Ingredientes),
        gama_marca(Marca, Gama),
        not((member(Com, Ingredientes), ingrediente_comedogenico(Com))),
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
