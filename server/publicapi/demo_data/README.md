
To populate the public API database with demo data, run the following command
in the console (from inside the `publicapi/demo_data` directory):

```sh
$ mongoimport -h localhost:27017 -d publicapi -c items --drop --file data.json
```

WARNING: any existing data in the `publicapi.items` collection gets removed.
