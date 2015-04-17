OBJ=thread_test
NUM=1
all:
	gcc -DNUM=${NUM} -pthread -fstack-protector-all ${OBJ}.c -o ${OBJ}

strong:
	gcc -DNUM=${NUM} -pthread -fstack-protector-strong ${OBJ}.c -o ${OBJ}
