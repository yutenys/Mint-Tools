import json
from web3 import Web3
from common import pbeWithMd5Des, loadEnv
import time

# 将 nonce 和 gas_price 声明为全局变量
global_nonce = None
global_gas_price = None

def interactWeb3(web3, nonce, gas_price, chainId, chainName, adress, data, private_key, gas_limit, multiple):
    print(f'公链：{chainName}   钱包地址：{adress}')
    print(f'当前gas价格:{gas_price / 1_000_000_000} gwei')
    currentGas = int(gas_price / 1_000_000_000)
    if gas_limit != '' and currentGas > int(gas_limit):
        return -1
    else:
        fibal_gas_price = int(float(gas_price) * multiple)
        tx = {
            'nonce': nonce,
            'chainId': chainId,
            'to': adress,
            'from': adress,
            'data': data,  # mint 16进制数据
            'gasPrice': fibal_gas_price,
            'value': Web3.to_wei(0, 'ether'),
            'gas':22200
        }
        print(f"交易消耗代币数量：{(tx['gasPrice'] / 1_000_000_000 * tx['gas']) / 1_000_000_000}")
        signed_tx = web3.eth.account.sign_transaction(tx, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        print(f'交易TX：{web3.to_hex(tx_hash)}')
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        return receipt.status


def mint(pwd):
    global global_nonce, global_gas_price
    delay, num, privateKey_env, adress, rpc, chainId, chainName, data, gas_limit, mulriple = loadEnv.loadDate()
    private_key = pbeWithMd5Des.decrypt_pbe_with_md5_and_des(pwd, privateKey_env)
    web3 = Web3(Web3.HTTPProvider(rpc))
    print(f'是否链接成功：{web3.is_connected()}')
    print(f'资产余额：{Web3.from_wei(web3.eth.get_balance(adress), "ether")}')
    success = 0
    failed = 0
    global_nonce = web3.eth.get_transaction_count(adress)
    global_gas_price = web3.eth.gas_price
    times = 0

    if num != '':
       # n = 0
        while success < int(num):
            web31 = Web3(Web3.HTTPProvider(rpc))
            try:
                if times != 0 and times % 100 == 0:
                    global_nonce = web31.eth.get_transaction_count(adress)
                    global_gas_price = web31.eth.gas_price

                else:
                    global_nonce = web31.eth.get_transaction_count(adress)
                    global_gas_price = web31.eth.gas_price

                    print('global_nonce:',global_nonce)
                    receipt = interactWeb3(web31, global_nonce, global_gas_price, chainId, chainName, adress, data, private_key,
                                           gas_limit,
                                           mulriple)
                    if receipt == -1:
                        print(F'~~~等待gas下降到{gas_limit}才铸造~~~')
                    elif receipt == 1:
                        success += 1
                        print("~~~Mint Success~~~")
                    else:
                        continue
            except Exception as e:
                print("~~~Mint Failed~~~")
                if str(e) == 'insufficient funds':
                    print("{chainName} 余额不足！")
                else:
                    print(f'Mint ERROR:{e}')
                failed += 1
            #n += 1
            times += 1
            global_nonce += 1
            print(F'{success} Success,{failed} Failed!\n\n')
            time.sleep(delay)
    else:
        while True:
            try:
                if times != 0 and times % 100 == 0:
                    global_nonce = web3.eth.get_transaction_count(adress)
                    global_gas_price = web3.eth.gas_price
                else:
                    receipt = interactWeb3(web3, global_nonce, global_gas_price, chainId, chainName, adress, data, private_key,
                                           gas_limit,
                                           mulriple)
                    if receipt == -1:
                        print(F'~~~等待gas下降到{gas_limit}才铸造~~~')
                    elif receipt == 1:
                        success += 1
                        print("~~~Mint Success~~~")
                    else:
                        continue
            except Exception as e:
                print("~~~Mint Failed~~~")
                if str(e) == 'insufficient funds for transfer':
                    print("{chainName} 余额不足！")
                else:
                    print(f'Mint ERROR:{e}')
                failed += 1
            times += 1
            global_nonce += 1
            print(F'{success} Success,{failed} Failed!\n\n')
            time.sleep(delay)
        print(f'成功：{success}\n失败:{failed}')
