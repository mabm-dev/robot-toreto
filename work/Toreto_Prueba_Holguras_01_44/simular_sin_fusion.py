"""Ejecuta el ensayo de la mano de 4 motores de punta a punta SIN Fusion.

Para qué sirve: comprobar, antes de pedirle al usuario una ejecución en
Fusion, que el código del ensayo no tiene errores de programación (nombres,
lógica, escritura del JSON). Se usó para la v7 y la v8, y ambas corrieron
bien a la primera en Fusion.

Qué NO hace: validar geometría. Sustituye `adsk` por un módulo falso; los
cuerpos no tienen forma real y los choques se INVENTAN a propósito (función
`penetration`) para que cada rama del ensayo se ejecute: un choque del cardán
al girar el pulgar, y las puntas de pulgar e índice tocándose al cerrar.
Un resultado "limpio" aquí no dice nada de la mano real.

Uso (desde esta carpeta):
    python simular_sin_fusion.py [salida.json]

Por defecto escribe en la carpeta temporal del sistema, no en el repo.
"""
import json
import math
import sys
import tempfile
import types
from pathlib import Path

SRC = Path(__file__).resolve().parent
sys.path.insert(0, str(SRC))


# ---------- adsk falso ----------
class P:
    def __init__(s, x=0, y=0, z=0): s.x, s.y, s.z = x, y, z


class Box:
    minPoint = P(-1, -1, -1)
    maxPoint = P(1, 1, 1)


class Mat:
    def setToRotation(s, rad, axis, center):
        s.deg = math.degrees(rad)
        return True


class Body:
    """Cuerpo falso: solo lleva su nombre y cuánto ha girado en total."""
    def __init__(s, label, closure=0.0):
        s.label, s.closure, s.volume = label, closure, 1.0
        s.isValid, s.boundingBox = True, Box()


class Mgr:
    def copy(s, b): return Body(b.label, b.closure)

    def transform(s, b, m):
        b.closure += abs(m.deg)
        return True

    def booleanOperation(s, target, tool, kind):
        target.volume = target.volume - penetration(target, tool) / 1000
        return True


def penetration(a, b):
    """Choques INVENTADOS para ejercitar cada rama del ensayo."""
    pair = {a.label, b.label}
    if pair == {'09_PULGAR_FALANGE_3', '07_DEDO_1_FALANGE_4'}:
        return max(0.0, a.closure + b.closure - 250)       # contacto de pinza
    if pair == {'09_PULGAR_CARDAN_INTERMEDIO', '10_PULGAR_NUDILLO_1_PASADOR'}:
        return 5.0 if max(a.closure, b.closure) > 20 else 0.0  # choque de mecanismo
    return 0.0


def _install_fake_adsk():
    measure = types.SimpleNamespace(
        measureMinimumDistance=lambda a, b: types.SimpleNamespace(
            value=max(0.0, (300 - a.closure - b.closure) / 100)))
    core = types.SimpleNamespace(
        Matrix3D=types.SimpleNamespace(create=Mat),
        Point3D=types.SimpleNamespace(create=P),
        Vector3D=types.SimpleNamespace(create=P),
        Application=types.SimpleNamespace(
            get=lambda: types.SimpleNamespace(measureManager=measure)))
    fusion = types.SimpleNamespace(
        BooleanTypes=types.SimpleNamespace(DifferenceBooleanType=1))
    adsk = types.ModuleType('adsk')
    adsk.core, adsk.fusion, adsk.doEvents = core, fusion, lambda: None
    sys.modules.update({'adsk': adsk, 'adsk.core': core, 'adsk.fusion': fusion})


def _fake_pending(hand, data):
    """Cuerpos falsos con los MISMOS nombres y grupos que el generador real."""
    specs = hand.joint_specs(data)
    pending = [(Body('06_PALMA_Y_CONECTOR'), '06_PALMA_Y_CONECTOR', '', 'MANO_00_PALMA')]
    for f in range(1, 5):
        for s in range(1, 5):
            label = f'07_DEDO_{f}_FALANGE_{s}'
            pending.append((Body(label), label, '', f'MANO_0{f}_FALANGE_0{s}'))
    pending.append((Body('09_PULGAR_CARDAN_INTERMEDIO'), '09_PULGAR_CARDAN_INTERMEDIO',
                    '', 'MANO_05_PULGAR_CARDAN'))
    for s in range(1, 4):
        label = f'09_PULGAR_FALANGE_{s}'
        pending.append((Body(label), label, '', f'MANO_05_PULGAR_FALANGE_0{s}'))
    for spec in specs:
        base = spec['pin_label'].replace('_PASADOR', '')
        for suffix in ('CASQUILLO_A', 'CASQUILLO_B', 'PASADOR', 'CASQUILLO_CENTRAL'):
            group = spec['child'] if suffix == 'CASQUILLO_CENTRAL' else spec['parent']
            pending.append((Body(f'{base}_{suffix}'), f'{base}_{suffix}', '', group))
    return pending


def main():
    _install_fake_adsk()
    import toreto_hand as hand
    import toreto_clearance as clearance
    import toreto_motor_groups as groups
    import toreto_motor_validation as validation

    data = json.loads((SRC / 'hand_local_sections.json').read_text())
    pending = _fake_pending(hand, data)
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else \
        Path(tempfile.gettempdir()) / 'toreto_simulacion_sin_fusion.json'
    report = validation.run(Mgr(), hand, clearance, groups, pending, data, out,
                            version='simulacion')

    print(f'Cuerpos simulados: {len(pending)} (palma excluida del ensayo)')
    print('Limites:', report['flexion_limits_deg'])
    print('Estado global:', report['status'], '(choques INVENTADOS a proposito)')
    print('Mano abierta  :', report['open_hand']['status'])
    for name, sc in report['scenarios'].items():
        print(f'  {name:22} {sc["status"]:28} moviles={sc["moving_bodies"]:3} '
              f'pares={sc["checked_pairs"]:5} choques={len(sc["pairs"])}')
    print('Contacto pinza:', report['scenarios']['pinza_boli']['pinch_contact'])
    json.loads(out.read_text(encoding='utf-8'))
    print('JSON escrito y legible:', out)


if __name__ == '__main__':
    main()
