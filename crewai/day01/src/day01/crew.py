from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

import os
from dotenv import load_dotenv
load_dotenv()

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

@CrewBase
class Day01:
	"""Day01 crew"""

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	@agent
	def joke_creator(self) -> Agent:
		return Agent(
			config=self.agents_config['joke_creator'],
			verbose=True
		)

	@agent
	def add_emojis(self) -> Agent:
		return Agent(
			config=self.agents_config['add_emojis'],
			verbose=True
		)

	@task
	def joke_task(self) -> Task:
		return Task(
			config=self.tasks_config['joke_task'],
		)

	@task
	def add_emojis_task(self) -> Task:
		return Task(
			config=self.tasks_config['add_emojis_task'],
			output_file='report.md'
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the Day01 crew"""
	
		return Crew(
			agents=self.agents, 
			tasks=self.tasks, 
			process=Process.sequential,
			verbose=True,
	
		)
