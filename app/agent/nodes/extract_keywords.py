import jieba.analyse
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.core.log import logger

def extract_keywords(state: DataAgentState, runtime:Runtime[DataAgentContext]):
    write=runtime.stream_writer
    write({'type':'progress','step':'抽取关键词','status':'running'})

    try :
        query = state['query']

        # 定义需要提取的词性（提升抽取效率）
        allow_pos = (
            "n",  # 名词: 数据、服务器、表格
            "nr",  # 人名: 张三、李四
            "ns",  # 地名: 北京、上海
            "nt",  # 机构团体名: 政府、学校、某公司
            "nz",  # 其他专有名词: Unicode、哈希算法、诺贝尔奖
            "v",  # 动词: 运行、开发
            "vn",  # 名动词: 工作、研究
            "a",  # 形容词: 美丽、快速
            "an",  # 名形词: 难度、合法性、复杂度
            "eng",  # 英文
            "i",  # 成语
            "l",  # 常用固定短语
        )

        keywords = jieba.analyse.extract_tags(query, allowPOS=allow_pos)

        result = list(set(keywords + [query]))
        logger.info(f'去重之后的提取关键词为: {result}')

        write({'type': 'progress', 'step': '抽取关键词', 'status': 'success'})

        return {"keywords": result}
    except Exception as e:
        logger.error(f'抽取关键词失败: {e}')
        write({'type': 'progress', 'step': '抽取关键词', 'status': 'error'})
        raise e