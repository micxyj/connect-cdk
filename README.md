# connect-cdk
cdk provision Amazon connect resources example

#### Build CDK env
```bash
npm install -g aws-cdk
cdk bootstrap aws://ACCOUNT-NUMBER/REGION
git clone https://github.com/micxyj/connect-cdk.git
cd connect-cdk
cdk init app --language python
python -m pip install -r requirements.txt
mv connect_cdk_stack.py connect_cdk/
```

#### Update connect_cdk_stack.py with your parameter

#### Deploying stack
```bash
cdk deploy
```

#### Destroying stack
```bash
cdk destroy
```
