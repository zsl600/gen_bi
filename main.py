import streamlit as st
from chain import NerveLLMChain
import traceback
import sqlparse
from langchain.callbacks.base import BaseCallbackHandler
from streamlit.elements.layouts import LayoutsMixin
from typing import Dict, Any, Union
from langchain.schema.agent import AgentAction,AgentFinish
import uuid
from googleapiclient.discovery import build

st.set_page_config(
    page_title="NERVE Q&A",
)

STARTING_MESSAGE = """
Hey there! I'm NERVE. Feel free to ask me anything!
Here are some of the questions you can ask:
1) What are the datasets available?
2) What is the total imports from China by Singapore in 2021?
"""

class AiProgressHandler(BaseCallbackHandler):
    def __init__(
        self,
        status:LayoutsMixin
    ) -> None:
        self.status = status
            
    def on_chain_start(
        self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    ) -> Any:
        """Run when chain starts running."""

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> Any:
        """Run when chain ends running."""

    def on_chain_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> Any:
        """Run when chain errors."""

    def on_tool_start(
        self, serialized: Dict[str, Any], input_str: str, **kwargs: Any
    ) -> Any:
        """Run when tool starts running."""

    def on_tool_end(self, output: str, **kwargs: Any) -> Any:
        """Run when tool ends running."""

    def on_tool_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> Any:
        """Run when tool errors."""

    def on_text(self, text: str, **kwargs: Any) -> Any:
        """Run on arbitrary text."""

    def on_agent_action(self, action: AgentAction, **kwargs: Any) -> Any:
        """Run on agent action."""
        self.status.update(label=f"Running {action.tool}...")

    def on_agent_finish(self, finish: AgentFinish, **kwargs: Any) -> Any:
        """Run on agent end."""


def check_password():
    return True




def on_input_change(user_input: str, sql_chain: NerveLLMChain, status_container: LayoutsMixin, chat_input_container: LayoutsMixin, clear_container: LayoutsMixin):
    user_input = user_input.strip()
    if user_input:
        st.session_state.chat_history.append({"type": "normal", "data": user_input, "role": "human"})
        status_update = status_container.status("Asking the chatbot...")
        clear_container.empty()
        callback = AiProgressHandler(status=status_update)
        try:
            result = sql_chain.run(user_input,callbacks=[callback])
            st.session_state.chat_history.append({"type": "normal", "data": result["output"], "role": "ai"})
            
            if result["image"]:
                st.session_state.chat_history.append({"type": "image", "data": result["image"], "role": "ai"})

            if result["sql_query"]:
                sql_query_string = f"""The following SQL query is used: 
~~~py
{sqlparse.format(result["sql_query"], reindent=True, keyword_case='upper')}
~~~
                    """
                st.session_state.chat_history.append({'type': 'normal', 'data': sql_query_string, 'role': 'ai'})
        except Exception as e:
            traceback.print_exc()
            st.session_state.chat_history.append({'type': 'normal', 'data': "I am unable to get the response based on this question, please fine-tune it before retrying", 'role': 'ai'})
        



def reset_history(sql_chain: NerveLLMChain):
    del st.session_state.chat_history[:]
    sql_chain.clear_memory()


def initialize():
    st.session_state.setdefault('chat_history',[])
    if "nerve_chain" not in st.session_state:
        st.session_state.setdefault('nerve_chain', NerveLLMChain(STARTING_MESSAGE, mock_data=True))
    if "session_id" not in st.session_state:
        st.session_state.setdefault('session_id', str(uuid.uuid4()))






def main():

    if check_password():
        st.title("Ask NERVE Anything")
        initialize()
        sql_chain = st.session_state.nerve_chain

        with st.container():   
            with st.chat_message("assistant"):
                st.write(STARTING_MESSAGE) 
            for i in range(len(st.session_state.chat_history)):     
                if st.session_state.chat_history[i]["role"] == "human":
                    with st.chat_message("user"):
                        st.write(st.session_state.chat_history[i]["data"])
                elif st.session_state.chat_history[i]["role"] == "ai":
                    with st.chat_message("assistant"):
                        if st.session_state.chat_history[i]["type"] == "normal":
                            st.write(st.session_state.chat_history[i]["data"])
                        elif st.session_state.chat_history[i]["type"] == "image":
                            st.image(st.session_state.chat_history[i]["data"])

        status_container = st.container().empty()

        chat_input_container = st.container().empty()

        clear_container = st.container().empty()

        clear_container.button("Clear message", on_click=reset_history, args=[sql_chain])
        
        user_input = st.chat_input(placeholder="What datasets do you have available?", key='real_chat_input')
        if user_input: 
            #streamlit will rerun after the callback is complete, hence any streamlit components that are modified within
            #this callback will be undone after it is done
            #hackish method which will break if chat_input is placed somewhere else
            st.chat_input(placeholder="What datasets do you have available?",disabled=True,key='disabled_chat_input')
            on_input_change(user_input, sql_chain, status_container, chat_input_container, clear_container)
            #Force rerun
            st.rerun()

        


if __name__ == "__main__":
    main()