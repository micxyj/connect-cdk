# connect-cdk
cdk provision Amazon connect resources example

#### Build CDK env
```bash
npm install -g aws-cdk
cdk bootstrap aws://ACCOUNT-NUMBER/REGION
git clone https://github.com/micxyj/connect-cdk.git
mkdir connect-cdk-example
cd connect-cdk-example
cdk init app --language python
python -m pip install -r requirements.txt
mv ../connect-cdk/connect_cdk_stack.py ./connect_cdk_example/
```

#### Update connect_cdk_stack.py 
Fill your parameters of connect

#### Deploying stack
```bash
cdk deploy
```

#### Destroying stack
```bash
cdk destroy
```
