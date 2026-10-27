# Apache Spark 3.2.1 Installation

Follow the steps below to install Apache Spark 3.2.1:

1. Download the Spark distribution package inside the designated directory using the following command:
    ```shell
    wget -P /path/to/streamline/spark https://archive.apache.org/dist/spark/spark-3.2.1/spark-3.2.1-bin-hadoop3.2.tgz
    ```

2. Extract the downloaded package using the following command:
    ```shell
    tar xvf /path/to/streamline/spark/spark-3.2.1-bin-hadoop3.2.tgz
    ```

3. Rename the extracted folder using the following command:
    ```shell
    mv /path/to/streamline/spark/spark-3.2.1-bin-hadoop3.2 /path/to/streamline/spark/spark-3.2.1
    ```

4. Update the `/root/.bashrc` file by adding the following lines:
    ```shell
    echo 'export SPARK_HOME=/path/to/streamline/spark/spark-3.2.1' | sudo tee -a /root/.bashrc
    echo 'export PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin' | sudo tee -a /root/.bashrc
    ```

5. Apply the changes made to the `/root/.bashrc` file by running the following command:
    ```shell
    sudo bash -c 'source /root/.bashrc'
    ```

That's it! You have successfully installed Apache Spark 3.2.1.
