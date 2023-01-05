Install **aws-cli** 

    sudo apt  install awscli

Now type

    aws configure

now add the following varibale values

    AWS Access Key ID [None]: **********
    AWS Secret Access Key [None]: **********
    Default region name [None]: ap-south-1
    Default output format [None]: json

now run

    ./backup.sh

in case of permission error

    chmod +rwx backup.sh