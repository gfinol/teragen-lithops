import argparse
import time

from lithops import FunctionExecutor, Storage
from lithops.config import load_config

from teragen.data_generator import DataGenerator


def size_str_to_bytes(s: str) -> int:
    lower = s.lower()
    if lower.endswith("k"):
        return int(lower[:-1]) * 1000
    elif lower.endswith("m"):
        return int(lower[:-1]) * 1000 * 1000
    elif lower.endswith("g"):
        return int(lower[:-1]) * 1000 * 1000 * 1000
    elif lower.endswith("t"):
        return int(lower[:-1]) * 1000 * 1000 * 1000 * 1000
    else:
        # no suffix, so it's just a number in bytes
        return int(lower)


def size_to_size_str(size):
    kb_scale = 1000
    mb_scale = 1000 * kb_scale
    gb_scale = 1000 * mb_scale
    tb_scale = 1000 * gb_scale

    if size > tb_scale:
        return str(size // tb_scale) + "TB"
    elif size > gb_scale:
        return str(size // gb_scale) + "GB"
    elif size > mb_scale:
        return str(size // mb_scale) + "MB"
    elif size > kb_scale:
        return str(size // kb_scale) + "KB"
    else:
        return str(size) + "B"


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("-s", "--size", required=True, type=str,
                    help="Size of the dataset to generate. Examples: 100k, 5m, 10g, 1t. Or just the number of bytes.")
    ap.add_argument("-b", "--bucket-name", type=str, help="Output bucket name", default="teragen-data")
    ap.add_argument("-k", "--key-name", type=str, help="Output file name", default="part-r")
    ap.add_argument("--ascii", action="store_true",
                    help="Generate ASCII data instead of binary data", default=False)
    ap.add_argument("-p", "--partitions", type=int, default=16,
                    help="Number of partitions to generate")
    ap.add_argument("-c", "--config-file", type=str)
    ap.add_argument("-l", "--localhost", action="store_true", default=False,
                    help="Run locally using processes")
    ap.add_argument("-u", "--unique-file", action="store_true", default=False,
                    help="Uses multipart upload to upload a unique file to S3. " +
                         "This needs Lithops configured with S3 as the storage backend.")

    return ap.parse_args()


def print_config(size, is_ascii, num_partitions, records_per_partition, num_records, key_name, bucket_name):
    print("===========================================================================")
    print("===========================================================================")
    print(f"Input size: {size_to_size_str(size)}")
    print(f"Total number of records: {num_records}")
    print(f"Number of output partitions: {num_partitions}")
    print(f"Number of records per partition: {records_per_partition}")
    print(f"Output format in ASCII: {is_ascii}")
    print(f"Output bucket: {bucket_name}")
    print(f"Output file name: {key_name}")
    print("===========================================================================")
    print("===========================================================================")


def write_dataset(index, records_per_partition, is_ascii, bucket_name, key_name, storage):
    dg = DataGenerator.create_data_generator(index, records_per_partition, is_ascii)
    start_time = time.time()
    storage.put_object(bucket_name, key_name, dg)
    end_time = time.time()

    return {'id': index, 'start_time': start_time, 'end_time': end_time}


def write_dataset_multipart(index, records_per_partition, is_ascii, bucket_name, key_name, upload_id, storage):
    dg = DataGenerator.create_data_generator(index, records_per_partition, is_ascii)
    start_time = time.time()
    client = storage.get_client()
    response = client.upload_part(Bucket=bucket_name, Key=key_name, PartNumber=index+1, UploadId=upload_id, Body=dg)
    end_time = time.time()
    part = {'PartNumber': index+1,
            'ETag': response['ETag']}
    return part


def main():
    args = parse_args()
    size = size_str_to_bytes(args.size)
    is_ascii = args.ascii
    key_name = args.key_name
    bucket_name = args.bucket_name
    num_partitions = args.partitions

    records_per_partition = size // num_partitions // 100
    num_records = records_per_partition * num_partitions

    print_config(size, is_ascii, num_partitions, records_per_partition, num_records, key_name, bucket_name)

    executor = FunctionExecutor(backend='localhost', storage='localhost') if args.localhost \
        else FunctionExecutor(config_file=args.config_file)

    if args.unique_file: # Create a single file
        if not (5 * 1024 * 1024 < records_per_partition * 100 < 5 * 1024 * 1024 * 1024):
            raise ValueError("Partition size must be between 5MB and 5GB for multipart upload.")

        client = Storage().get_client()
        multipart_response = client.create_multipart_upload(Bucket=bucket_name, Key=key_name)
        upload_id = multipart_response['UploadId']
        arg_iter = [(i, records_per_partition, is_ascii, bucket_name, key_name, upload_id)
                    for i in range(num_partitions)]
        executor.map(write_dataset_multipart, arg_iter)
        parts = executor.get_result()

        client.complete_multipart_upload(Bucket=bucket_name, Key=key_name, UploadId=upload_id,
                                         MultipartUpload={'Parts': parts})

    else: # Create multiple files
        arg_iter = [(i, records_per_partition, is_ascii, bucket_name, f"{key_name}-{i:05d}")
                    for i in range(num_partitions)]
        executor.map(write_dataset, arg_iter)
        executor.wait()


    print("===========================================================================")
    print("Data generation complete")
    print("===========================================================================")



if '__main__' == __name__:
    main()