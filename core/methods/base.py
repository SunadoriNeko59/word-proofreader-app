from abc import ABC, abstractmethod
from typing import List, Dict

class BaseProofreader(ABC):
    """
    添削手法の基底インターフェース
    """

    @abstractmethod
    def proofread(self, text: str) -> List[Dict[str, str]]:
        """
        テキストの添削を行います。
        
        Args:
            text (str): 添削対象のテキスト全体
            
        Returns:
            List[Dict[str, str]]: 修正箇所のリスト。各要素は以下の形式の辞書
            {
                "original": "修正前の文字列",
                "corrected": "修正後の文字列",
                "reason": "修正理由"
            }
        """
        pass
