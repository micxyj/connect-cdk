# connect-cdk
cdk provision Amazon connect resources example

#### Build CDK env
```bash
pip install streamlit
npm install -g aws-cdk
cdk bootstrap aws://ACCOUNT-NUMBER/REGION
git clone https://github.com/micxyj/connect-cdk.git
mkdir connect-cdk-example
cd connect-cdk-example
cdk init app --language python
python -m pip install -r requirements.txt
mv ../connect-cdk/connect_cdk_stack.py ./connect_cdk_example/connect_cdk_example_stack.py
mv ../connect-cdk/app.py ./app.py
mv ../connect-cdk/logo.png ./logo.png
```

#### Update connect_cdk_example_stack.py 
Fill your parameters of connect

#### Running Streamlit APP
```bash
cd connect_cdk_example
streamlit run connect_cdk_example_stack.py
```
