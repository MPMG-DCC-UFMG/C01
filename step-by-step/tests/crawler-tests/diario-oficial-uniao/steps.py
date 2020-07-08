import step_crawler
from step_crawler.functions_file import *

async def execute_steps(**missing_arguments):
    await clique(**missing_arguments, xpath = '//*[@id="banner"]/div[1]/div[2]/div[1]/div/div/ul/li[3]/a')
    await clique(**missing_arguments, xpath = '//*[@id="portlet_leituradou_INSTANCE_GKE7NRmaCXgl"]/div/div[2]/div/div[1]/div[3]/button[4]')
    espere(segs = 3)
