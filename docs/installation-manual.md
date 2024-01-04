![](./logo.png)

# Stargazer Framework installation manual

---

Stargaze Framework is built with Docker in mind.

Scientific datacenters require frequent upgrades to keep up with technological requirements, and such upgrades imply downtimes, difficult architectural accomodations, and an overall large effort from all involved parties to be successful.

Docker - and container technology in general - allows for hardware abstraction and fixes most of the issues with traditional HPC. This is the reason why Stargazer is distributed with Docker.

## Docker images

Several Docker images are provided:

- `chelsea486mhz/stargazer-auth`: Authentication gateway
- `chelsea486mhz/stargazer-manager`: Manager node
- `chelsea486mhz/stargazer-compute`: Compute node

## Topology

The absolute minimum configuration for a Stargazer Framework consists of an authentication gateway, a manager, and a compute node.

Since the Stargazer protocol is entirely based around an HTTP API, it is recommended to make the authentication gateway highly available using your favorite proxy.

A single compute node can be registered to different managers: this allows for concurrent simulations to use all available hardware, instead of imposing hard partitions. However, this should be done carefuly so as to not cause disproportionate denial of service. This use case has small simulations in mind.

As such, my personal recommendation is to run a single manager and properly schedule simulation runs.

## Deployments

Example deployments are provided in the `deployments` folder at the root of the repository.