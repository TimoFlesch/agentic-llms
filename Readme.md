# Agentic LLMs
This little Python library turns an LLM that is running locally on your machine into an agent that can use tools (web search, Linux Shell, Python REPL, Wikipedia) to solve problems. My goal was to write a minimum working example to study tool-use and planning abilities of LLMs, drawing inspiration from [LangChain](https://www.langchain.com/) and [M.Paepper's minimal agent](https://www.paepper.com/blog/posts/intelligent-agents-guided-by-llms/).



### LLMs
The repository relies on [GPT4ALL](https://github.com/nomic-ai/gpt4all), a toolbox that allows you to run highly quantized LLMs locally on your CPU. I decided against implementing an openAI(or the like) API connection, as I wanted to be able to run everything locally and test the boundaries of publicly available models. 
By default, Agentic_LLMs uses `Mistral-7B`, which can be downloaded from the following link: https://gpt4all.io/models/gguf/mistral-7b-instruct-v0.1.Q4_0.gguf

### Tools
The following tools have been implemented:
1. `DDGSearch`: Searches [duckduckgo.com](https://duckduckgo.com) and returns top n results
1. `WikipediaSummary`: Searches [Wikipedia](https://en.wikipedia.org/wiki/Main_Page) and returns summaries for top n results.
1. `PythonInterpreter`: Launches [Docker](docker.com) container with [Python](python.org) interpreter (so that it's isolated from host system) and executes python commands and code-snippets. Automatically converts multiline code snippets into executable commands. Returns results.
1. `LinuxShell`: Launches [Docker](docker.com) container with [Alpine Linux](https://www.alpinelinux.org/) shell (so that it's isolated from host system) and executes linux commands.


### Safety 
The Toolbox executes Python and Linux commands received from the LLM inside Docker containers that are created and managed on the fly. Containers can be configured to be either persistent (active throughout session) or not (stopped after command execution).


### How it works 
Following [M.Paepper's wonderful blog post](https://www.paepper.com/blog/posts/intelligent-agents-guided-by-llms/), I im[lemented a variant of [ReAct prompting](https://arxiv.org/abs/2210.03629). The agent is given the following system prompt:
```
Today is {today} and you can use tools to get new information.
Answer the question as best as you can using the following tools: 

{tool_description}


Use the following format:

Question: the input question you must answer
Thought: comment on what you want to do next
Action: the action to take, exactly one element of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation repeats N times, 
use it until you are sure of the answer)
Thought: I now know the final answer
Final Answer: your final answer to the original input question

Begin!

Question: {question}
Thought: {previous_responses}
```

After it was provided with a `Question`, the agent's LLM generates pairs of `Action` (denoting the tool to use) and `Action Input` (denoting the input to the tool). The agent then sends `Action Input` to the tool `Action`, and receives a result `Observation`. This result is fed back into the LLM, together with the history of previous interactions, and the procedure repeats. The agent is prompted to give a final answer with the `Final Answer` prefix once it's confident that the `Observation` answers the `Question`. This will terminate the loop. As the agent tends to hallucinate the Observation itself, we stop generation once the agent has returned the `Observation` keyword.


### Installation Instructions
1. Install [Docker](docker.com) . Make sure that you've got a working version of docker running in the background!
2. Download Mistral-7B from the following link https://gpt4all.io/models/gguf/mistral-7b-instruct-v0.1.Q4_0.gguf and put it in the `./models/` subfolder
3. Make a copy of `configs/default_config.json` and update the model_path so that it points to the folder containing Mistral-7B (e.g. `/home/USER/code/agentic-llm/models`)
4. From within the project folder,  run `pip install -e .` to install the package
5. in your CLI, run `agentic_llm --help` to make sure that everything works. You should see the following output:

```
Usage: agentic_llm [OPTIONS]

  An AI agent that uses tools to answer your questions

Options:
  --config_path TEXT  path to config file, e.g. /home/USER/code/agentic-
                      llm/configs/default_config.json. Uses default config if
                      left empty
  --query TEXT        A question for the agent
  --help              Show this message and exit.
  ```

### How to Use
Example usage is detailed in `notebooks/example.ipynb`. Alternatively, you can use the command-line interface as follows:

```
$ agentic_llm --config_path ${PATH_TO_CONFIG_DIR}/default_config.json
Your Query: <ENTER YOUR QUERY HERE>
```

### Showcase
Results are mixed... When instructed to use a specific tool, it will do so:
```


Question: Use Python to calculate: what is 7*7+4?
Thought: 
            
 Action: Python Interpreter
Action Input: `print(7*7+4)`

Observation: 53

 Thought:
 I now know the final answer.
Final Answer: 53

```
 It will also use other tools at its disposal to obtain further information:
 ```

Question: Use Python to calculate the first 4 fibonacci numbers.
Thought: 
            
 Action: Python Interpreter
Action Input: `print(fibonacci(10))`

Observation: Execution Failed! Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "<string>", line 1, in <module>
NameError: name 'fibonacci' is not defined

 Thought:
 Action: DuckDuckGo Search
Action Input: "Fibonacci function"

Observation: {'title': 'Fibonacci sequence - Wikipedia', 'answer': 'A tiling with squares whose side lengths are successive Fibonacci numbers: 1, 1, 2, 3, 5, 8, 13 and 21. In mathematics, the Fibonacci sequence is a sequence in which each number is the sum of the two preceding ones. Numbers that are part of the Fibonacci sequence are known as Fibonacci numbers, commonly denoted F n .The sequence commonly starts from 0 and 1, although some authors start the ...'}
{'title': 'Fibonacci Series - GeeksforGeeks', 'answer': 'Complexity Analysis. Time Complexity: O(n), Because for n number for terms, the loop inside the printFib() function will be executed n times.; Auxiliary Space: O(1), Because we only used a few variables which don't depends on the number of terms to be printed; Relation Between Pascal triangle and Fibonacci numbers:. Pascal's triangle is the arrangement of the data in triangular form which ...'}

 Thought:
[...]
 
 ```

 But often, its line of reasoning isn't particularly sound (which might have something to do with the short context window of locally hosted models):
 ```
 
Today is 2024-01-16 and you can use tools to get new information.
Answer the question as best as you can using the following tools: 

DDG Search: Get information for a search query. Input should be either a question like 'Who was Tolstoy?', or a single word like 'Tolstoy'. Result will be the answers to the question. There can be multiple results. 
Linux Shell: A Linux Shell. Use this to execute Linux commands. Input should be valid Linux commands. Chain several commands together with semicolon. Missing packages can be installed with `apk add ...` 
Python Interpreter: A Python interpreter. Use this to execute python code. Input should be valid python code. If you want to see the output of a value, you should print it out with `print(...)`
Wikipedia: Get information from an encyclopedia to answer a search query. Input should be a search query such as 'Who was Marie Curie?'. Result will be a detailed answer to the question. There can be multiple results. 


Use the following format:

Question: the input question you must answer
Thought: comment on what you want to do next
Action: the action to take, exactly one element of [DuckDuckGo Search, Linux Shell, Python Interpreter, Wikipedia]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation repeats N times, 
use it until you are sure of the answer)
Thought: I now know the final answer
Final Answer: your final answer to the original input question

Begin!

Question: Use Wikipedia to tell me where and when Alan Turing was born
Thought: 
            

Action: Wikipedia
Action Input: Alan Turing

Observation: {'title': 'Alan Turing', 'summary': 'Alan Mathison Turing  (; 23 June 1912 – 7 June 1954) was an English mathematician, computer scientist, logician, cryptanalyst, philosopher and theoretical biologist. Turing was highly influential in the development of theoretical computer science, providing a formalisation of the concepts of algorithm and computation with the Turing machine, which can be considered a model of a general-purpose computer. He is widely considered to be the father of theoretical computer science and artificial intelligence.Born in Maida Vale, London, Turing was raised in southern England. He graduated at King\'s College, Cambridge, with a degree in mathematics. Whilst he was a fellow at Cambridge, he published a proof demonstrating that some purely mathematical yes–no questions can never be answered by computation. He defined a Turing machine and proved that the halting problem for Turing machines is undecidable. In 1938, he obtained his PhD from the Department of Mathematics at Princeton University.\nDuring the Second World War, Turing worked for the Government Code and Cypher School at Bletchley Park, Britain\'s codebreaking centre that produced Ultra intelligence. For a time he led Hut 8, the section that was [...], 'source': 'https://en.wikipedia.org/wiki/Alan_Turing'}
 Thought:
 Action: DuckDuckGo Search
             Action Input: Where was Alan Turing born?


Observation: {'title': 'Alan Turing - Wikipedia', 'answer': 'Turing was born in Maida Vale, London, while his father, Julius Mathison Turing was on leave from his position with the Indian Civil Service (ICS) of the British Raj government at Chatrapur, then in the Madras Presidency and presently in Odisha state, in India.'}
{'title': 'Alan Turing | Biography, Facts, Computer, Machine ... - Britannica', 'answer': 'Alan Turing (born June 23, 1912, London, England—died June 7, 1954, Wilmslow, Cheshire) British mathematician and logician who made major contributions to mathematics, cryptanalysis, logic, philosophy, and mathematical biology and also to the new areas later named computer science, cognitive science, artificial intelligence, and artificial life.'}
{'title': 'Alan Turing — Complete Biography, History and Inventions', 'answer': 'Though he was born in Maida Vale, London, Turing grew up in southern England. He graduated with a degree in mathematics from King's College at Cambridge University and published an unprovable theorem demonstrating that some mathematical questions can never be answered by computation.'}
 Thought:
 Action: Python Interpreter
                     Action Input: Where was Alan Turing born?
                     
Observation: Execution Failed! Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "<string>", line 1
    Where was Alan Turing born?
          ^
SyntaxError: invalid syntax

 Thought:

 ```

 Another example:
 ```
 

Question: Use Linux to tell me your ip address
Thought: 
            
 Action: Linux Shell
Action Input: `ifconfig`

Observation: eth0      Link encap:Ethernet  HWaddr <REDACTED>
          inet addr:<REDACTED>  Bcast:<REDACTED>  Mask:<REDACTED>
          UP BROADCAST RUNNING MULTICAST  MTU:<REDACTED>  Metric:1
          RX packets:<REDACTED> errors:<REDACTED> dropped:<REDACTED> overruns:<REDACTED> frame:<REDACTED>
          TX packets:<REDACTED> errors:<REDACTED> dropped:<REDACTED> overruns:<REDACTED> carrier:<REDACTED>
          collisions:<REDACTED> txqueuelen:<REDACTED> 
          RX bytes:<REDACTED>  TX bytes:<REDACTED>

lo        Link encap:Local Loopback  
          inet addr:<REDACTED>  Mask:<REDACTED>
          UP LOOPBACK RUNNING  MTU:<REDACTED>  Metric:1
          RX packets:<REDACTED> errors:<REDACTED> dropped:<REDACTED> overruns:<REDACTED> frame:<REDACTED>
          TX packets:<REDACTED> errors:<REDACTED> dropped:<REDACTED> overruns:<REDACTED> carrier:<REDACTED>
          collisions:<REDACTED> txqueuelen:<REDACTED> 
          RX bytes:<REDACTED>  TX bytes:<REDACTED>


 Thought:
 Action: DuckDuckGo Search
             Action Input: 'ip address'


Observation: {'title': 'IP Address Lookup - Check Location of Your Public IP', 'answer': 'IP Location Lookup tool provides free location tracking of an entered IP Address. It instantly tracks the IP's city, country, latitude, and longitude data through various Geo IP Databases. If you are concerned about the GeoLocation data accuracy for the data listed below, please review the GeoLocation accuracy information for clarification.'}
{'title': 'What Is an IP Address? - Lifewire', 'answer': 'An IP address, short for Internet Protocol address, is an identifying number for network hardware connected to a network. Having an IP address allows a device to communicate with other devices over an IP-based network like the internet. What Does an IP Address Look Like? Most IP addresses look like this: 151.101.65.121'}
{'title': 'What is an IP Address? - GeeksforGeeks', 'answer': 'What is an IP Address? Read Courses All the computers of the world on the Internet network communicate with each other with underground or underwater cables or wirelessly.'}
 Thought:
 Action: Wikipedia
              Action Input: 'IP address'


Observation: {'title': 'IP address', 'summary': 'An Internet Protocol address (IP address) is a numerical label such as 192.0.2.1 that is assigned to a device connected to a computer network that uses the Internet Protocol for communication. IP addresses serve two main functions: network interface identification, and location addressing.\nInternet Protocol version 4 (IPv4) defines an IP address as a 32-bit number. However, because of the growth of the Internet and the depletion of available IPv4 addresses, a new version of IP (IPv6), using 128 bits for the IP address, was standardized in 1998. IPv6 deployment has been ongoing since the mid-2000s.\nIP addresses are written and displayed in human-readable notations, such as 192.0.2.1 in IPv4, and 2001:db8:0:1234:0:567:8:1 in IPv6. The size of the routing prefix of the address is designated in CIDR notation by suffixing the address with the number of significant bits, e.g., 192.0.2.1/24, which is equivalent to the historically used subnet mask 255.255.255.0.\nThe IP address space is managed globally by the Internet Assigned Numbers Authority (IANA), and by five regional Internet registries (RIRs) responsible in their designated territories for assignment to local Internet registries, such as Internet service providers (ISPs), and other end users. IPv4 addresses were distributed by IANA to the RIRs in blocks of approximately 16.8 million addresses each, but have been exhausted at the IANA level since 2011. Only one of the RIRs still has a supply for local assignments in Africa. Some IPv4 addresses are reserved for private networks and are not globally unique.\nNetwork administrators assign an IP address to each device connected to a network. Such assignments may be on a static (fixed or permanent) or dynamic basis, depending on network practices and software features.\n\n', 'source': 'https://en.wikipedia.org/wiki/IP_address'}
 Thought:
 Action: Python Interpreter
                     Action Input: `print(input("What is your ip address?"))`



Observation: Execution Failed! What is your ip address?Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "<string>", line 1, in <module>
EOFError: EOF when reading a line

 Thought:
 Action: DuckDuckGo Search
                     Action Input: 'ip address'



Observation: {'title': 'IP Address Lookup - Check Location of Your Public IP', 'answer': 'IP Location Lookup tool provides free location tracking of an entered IP Address. It instantly tracks the IP's city, country, latitude, and longitude data through various Geo IP Databases. If you are concerned about the GeoLocation data accuracy for the data listed below, please review the GeoLocation accuracy information for clarification.'}
{'title': 'What Is an IP Address? - Lifewire', 'answer': 'An IP address, short for Internet Protocol address, is an identifying number for network hardware connected to a network. Having an IP address allows a device to communicate with other devices over an IP-based network like the internet. What Does an IP Address Look Like? Most IP addresses look like this: 151.101.65.121'}
{'title': 'What is an IP Address? - GeeksforGeeks', 'answer': 'What is an IP Address? Read Courses All the computers of the world on the Internet network communicate with each other with underground or underwater cables or wirelessly.'}
 Thought:
stopping container python_repl...
...done!
stopping container linux_repl...
...done!
None

 ```
