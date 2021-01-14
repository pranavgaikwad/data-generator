# Data Generator

This is a collection of tools to generate random sample data in a given directory and simulate file operations on the generated data. 

The suite of tools can be deployed on a Kubernetes cluster using the provided [Ansible Playbook](#deploy-on-kubernetes). 

## Generating sample data

[file-generator.py](./file-generator.py) is a Python program that generates sample data in any given directory. It uses following command line arguments:

| Argument             	| Type   	| Required 	| Description                                                           	|
|----------------------	|--------	|----------	|-----------------------------------------------------------------------	|
| --size <size>        	| string 	| Yes      	| Total size of random data to create in supported units: b,Ki,Mi,Gi,Ti 	|
| --max-files <number> 	| int    	| Yes      	| Maximum number of files to create                                     	|
| --min-files <number> 	| int    	| No       	| Minimum number of files to create (Defaults to 1)                     	|
| --dest-dir <dir>     	| string 	| Yes      	| Destination directory for generated data                              	|
| --help, -h           	| -      	| No       	| Print help                                                            	|

When `--min-files` and `--max-files` are provided, the program spreads the total size `--size` over number of files in the range [min-files, max-files].

## Simulating operations on sample data

[file-operations.py](./file-operations.py) is a Python program that performs different file operations on files in the given directory. The operations are performed randomly.

The supported file operations are:
- Creating a new file
- Appending data to an existing file
- Deleting an existing file
- Removing bytes from an existing file
- Changing permissions on an existing file

It uses following command line arguments:

| Argument         	| Type   	| Required 	| Description                                                             	|
|------------------	|--------	|----------	|-------------------------------------------------------------------------	|
| --buffer <size>  	| string 	| Yes      	| Extra wiggle room for file operations in supported units: b,Ki,Mi,Gi,Ti 	|
| --dest-dir <dir> 	| string 	| Yes      	| Destination directory for generated data                                	|
| --help, -h       	| -      	| No       	| Print help                                                              	|

In some of the file operations, the program may create additional data in existing files. `--buffer` option allows setting an upper limit on the additional data created by the program. 

Sometimes, you might want to pause the file operations. You can do that by setting `PAUSE_OPERATIONS` environment variable to `True`. The operations will resume when it is set to `False`.  

The file operations has a scanner thread running in the background which periodically updates the list of the files. You can set a custom time interval for scanner using `SCANNER_INTERVAL` environment variable. By default, it is set to `120` in seconds. If the destination directory contains a huge number of files, consider setting this to a higher value. For Kubernetes deployment, both of the above environment variables are passed through configmap `settings`:

```yml
kind: ConfigMap
apiVersion: v1
metadata:
  name: settings
data:
  OPERATOR_PAUSE: False
  SCANNER_INTERVAL: 600
```

## Deploy on Kubernetes

To deploy the above workloads on a Kubernetes cluster, simply run the [Ansible Playbook](./playbook.yml):

```sh
ansible-playbook playbook.yml
```

The above playbook will create a Pod with 2 containers, one of them runs [file-generator.py](./file-generator.py) to create random data in a Persistent Volume, while the other one runs [file-operations.py](./file-operations.py) to perform random operations on the generated data.

The playbook uses [defaults.yml](./defaults.yml) for configuration. Here are the available options to configure the playbook:

| Variable  	| Description                                                                                        	|
|-----------	|----------------------------------------------------------------------------------------------------	|
| file_size 	| Sets [--size](#generating-sample-data) option                                                      	|
| max_files 	| Sets [--max-files](#generating-sample-data) option                                                 	|
| min_files 	| Sets [--min-files](#generating-sample-data) option                                                 	|
| pvc_size  	| Size of volume (needs to be greater than or equal to file_size option)                             	|
| buffer    	| Sets [--buffer](#simulating-operations-on-sample-data) option                                      	|
| namespace 	| Namespace for workload                                                                             	|
| pod_name  	| Name of the workload pod                                                                           	|
| image     	| Workload docker image (See [this section](#build-your-own-workload-image) to build your own image) 	|
| destroy   	| Deletes the workload when set to `true`                                                            	|

## Build your own workload image

To build your own image, simply run:

```sh
docker build -t <your_image> -f Dockerfile .
```

To push, run:

```sh
docker push <your_image>
```

Use `image` variable to use your own image in [Ansible Playbook](#deploy-on-kubernetes) for the workload.