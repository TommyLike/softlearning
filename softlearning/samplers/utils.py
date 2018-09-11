import time

import numpy as np


def rollout(env,
            policy,
            path_length,
            render=False,
            callback=None,
            render_mode='human',
            break_on_terminal=True):
    images = []

    observation_shape = env.observation_space.shape
    action_shape = env.action_space.shape

    assert len(observation_shape) == 1, observation_shape
    Do = observation_shape[0]
    assert len(action_shape) == 1, action_shape
    Da = action_shape[0]

    observation = env.reset()
    policy.reset()

    observations = np.zeros((path_length + 1, Do))
    actions = np.zeros((path_length, Da))
    terminals = np.zeros((path_length, ))
    rewards = np.zeros((path_length, ))
    agent_infos = []
    env_infos = []

    t = 0  # To make edge case path_length=0 work.
    for t in range(path_length):
        (action, _, _), agent_info = policy.get_action(observation)

        if callback is not None:
            callback(observation, action)

        next_obs, reward, terminal, env_info = env.step(action)

        agent_infos.append(agent_info)
        env_infos.append(env_info)

        actions[t] = action
        terminals[t] = terminal
        rewards[t] = reward
        observations[t] = observation

        observation = next_obs

        if render:
            if render_mode == 'rgb_array':
                image = env.render(mode=render_mode)
                images.append(image)
            else:
                env.render()

        if terminal:
            if break_on_terminal: break

            observation = env.reset()
            policy.reset()

    observations[t + 1] = observation

    path = {
        'observations': observations[:t + 1],
        'actions': actions[:t + 1],
        'rewards': rewards[:t + 1],
        'terminals': terminals[:t + 1],
        'next_observations': observations[1:t + 2],
        'agent_infos': agent_infos,
        'env_infos': env_infos
    }

    if render_mode == 'rgb_array':
        path['images'] = np.stack(images, axis=0)

    return path


def rollouts(env, policy, path_length, n_paths, render=False,
             render_mode='human'):
    paths = [
        rollout(env, policy, path_length, render, render_mode=render_mode)
        for i in range(n_paths)
    ]

    return paths
