from hermes.blood_pressure import blood_pressure_pod
from hermes.wheke import Hermes

hermes = Hermes()
hermes.add_pod(blood_pressure_pod)

app = hermes.create_app()
