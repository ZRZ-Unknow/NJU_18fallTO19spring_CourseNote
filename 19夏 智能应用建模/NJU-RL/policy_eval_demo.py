import numpy as np
import sys
if "../" not in sys.path:
  sys.path.append("../")
from lib.envs.gridworld import GridworldEnv

# change step size
STEP_SIZE = 10
env = GridworldEnv()


def policy_eval(policy, env, discount_factor=1.0, theta=0.00001, iter_cnt=0):
    """
    Evaluate a policy given an environment and a full description of the environment's dynamics.

    Args:
        policy: [S, A] shaped matrix representing the policy.
        env: OpenAI env. env.P represents the transition probabilities of the environment.
            env.P[s][a] is a list of transition tuples (prob, next_state, reward, done).
            env.nS is a number of states in the environment.
            env.nA is a number of actions in the environment.
        theta: We stop evaluation once our value function change is less than theta for all states.
        discount_factor: Gamma discount factor.

    Returns:
        Vector of length env.nS representing the value function.
    """
    # Start with a random (all 0) value function
    V = np.zeros(env.nS)
    V_cache = np.zeros(env.nS)
    while True:
        delta = 0
        # For each state, perform a "full backup"
        for s in range(env.nS):
            v = 0
            # Look at the possible next actions
            for a, action_prob in enumerate(policy[s]):
                # For each action, look at the possible next states...
                for prob, next_state, reward, done in env.P[s][a]:
                    # Calculate the expected value. Ref: Sutton book eq. 4.6.
                    v += action_prob * prob * (reward + discount_factor * V[next_state])
                    print('--------------------------------------',action_prob,prob)
            print('v是',v)
            # How much our value function changed (across any states)
            delta = max(delta, np.abs(v - V[s]))
            V_cache[s] = v
        V = V_cache
        # Stop evaluating once our value function change is below a threshold
        if delta < theta:
            break

        if iter_cnt % STEP_SIZE == 0:
            print("current itertion is:", iter_cnt)
            print(V.reshape(env.shape))
            print("\n")
        iter_cnt += 1
    return np.array(V), iter_cnt

random_policy = np.ones([env.nS, env.nA]) / env.nA
print("random policy:", random_policy)

v, iter_cnt = policy_eval(random_policy, env)

print("iter count:", iter_cnt)

print("Reshaped Grid Value Function:")
print(v.reshape(env.shape))
print("")