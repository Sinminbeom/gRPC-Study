import os
import subprocess


def run_shell_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    output, error = process.communicate()

    if error:
        print(f"Error: {error}")


if __name__ == '__main__':

    if not os.path.exists('../Client/Protos'):
        os.makedirs('../Client/Protos')

    if not os.path.exists('../Server/Protos'):
        os.makedirs('../Server/Protos')

    run_shell_command('python -m grpc_tools.protoc '
                      '-I../Schema '
                      '--python_out=../Client/Protos '
                      '--pyi_out=../Client/Protos '
                      '--grpc_python_out=../Client/Protos '
                      '../Schema/chat.proto')

    run_shell_command('python -m grpc_tools.protoc '
                      '-I../Schema '
                      '--python_out=../Server/Protos '
                      '--pyi_out=../Server/Protos '
                      '--grpc_python_out=../Server/Protos '
                      '../Schema/chat.proto')

