cp ../../fido/fido.py ./fido/
cp ../../fido/argparselocal.py ./fido/
javac Main.java -d .
jar -cfe ../fido.jar Main com fido javatests jline Lib Main.class META-INF org
