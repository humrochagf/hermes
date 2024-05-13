from hermes.blood_pressure.pod import blood_pressure_pod
from hermes.core.pod import core_pod
from hermes.wheke import Hermes

hermes = Hermes()
hermes.add_pod(core_pod)
hermes.add_pod(blood_pressure_pod)

app = hermes.create_app()
