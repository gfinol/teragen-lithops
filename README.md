# TeraSort dataset creator for Python
This is a python implementation of TeraGen using Lithops. It generates a dataset for the [sort benchmark](https://sortbenchmark.org/). 
This implementation creates the dataset using FaaS and stores it in an object storage. The dataset is created in parallel using Lithops. 
It has been inspired by the [hadoop implementation](https://github.com/apache/hadoop/blob/trunk/hadoop-mapreduce-project/hadoop-mapreduce-examples/src/main/java/org/apache/hadoop/examples/terasort/TeraGen.java) and this [spark implementation](https://github.com/ehiggs/spark-terasort). 


## Install dependencies
The only dependency is [Lithops](https://github.com/lithops-cloud/lithops). You can install it using pip:

```bash
pip3 install lithops
```
or using the requirements.txt file:

```bash
pip3 install -r requirements.txt
```

## Set up
You need to set up the [config file](https://lithops-cloud.github.io/docs/source/configuration.html#configuration-file) for Lithops. 
You can find a template in the [Lithops repository](https://github.com/lithops-cloud/lithops/blob/master/config/config_template.yaml).

## Usage
You can run the [teragen.py](teragen.py) script using the following command:

```bash
python3 teragen.py -s <size> -b <bucket> -k <key> -p <partitions> -c <config_file>
```

## Parameters
The script takes the following parameters:
- **-s**: Size of the dataset to generate. Examples: 100k, 5m, 10g, 1t. Or just the number of bytes.
- **-b**: Bucket name to store the dataset.
- **-k**: Key name prefix for the files created.
- **-p**: Number of partitions files to create. Lithops will create a worker for each partition.
- **-c**: Lithops config file path
- **--ascii**: Use only printable characters in the dataset. Default: False
- **--localhost** Execute the function locally using processes. Default: False
- **-h**: Show help message.
- **--unique-file**: Create a unique file instead of multiple files. Uses S3 multipart upload. 
Requires S3 as the configured Lithops storage backend. Default: False