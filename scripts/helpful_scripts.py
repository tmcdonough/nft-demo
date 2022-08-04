from brownie import accounts, network, config, LinkToken, VRFCoordinatorMock, Contract
from web3 import Web3

LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["hardhat", "development", "ganache"]
OPENSEA_URL = "https://testnets.opensea.io/assets"
BREED_MAPPING = {0: "PUG", 1: "SHIBA_INU", 2: "ST_BERNARD"}


def get_breed(breed_number):
    return BREED_MAPPING[breed_number]


def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return accounts[0]
    if id:
        return accounts.load(id)
    return accounts.add(config["wallets"]["from_key"])


contract_to_mock = {"link_token": LinkToken, "vrf_coordinator": VRFCoordinatorMock}


def get_contract(contract_name):
    """
    This function will either:
     - Get an address from the config (for a livenet)
     - Deploy a mock (for local)

     Args:
     - contract_name (string): name of the contract that we are pulling

     Returns:
     - brownie.network.contract.ProjectContract: the most recently deployed contract of this type
    """

    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) == 0:
            deploy_mocks()
        contract = contract_type[-1]
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )
    return contract


def deploy_mocks():
    account = get_account()
    link_token = LinkToken.deploy({"from": account})
    vrf_coordinator = VRFCoordinatorMock.deploy(link_token.address, {"from": account})


def fund_with_link(
    contract_address, account=None, link_token=None, amount=Web3.toWei(1, "ether")
):
    amount_in_ether = Web3.fromWei(amount, "ether")
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    funding_tx = link_token.transfer(
        contract_address, amount, {"from": account, "required_confs": 1}
    )
    funding_tx.wait(1)
    print(f"Funded {contract_address} with {amount_in_ether} LINK")
    return funding_tx
