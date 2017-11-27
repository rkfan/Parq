prospector *.py --uses flask --profile profile.yaml >output.txt
prospector app/*.py --uses flask --profile profile.yaml >>output.txt
prospector app/tests/*.py --uses flask --profile profile.yaml >>output.txt