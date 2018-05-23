import hashlib


class Leaf(object):

  def __init__(self, position, key=None, value=None, hash_digest=None):
    self.key = key
    self.value = value
    self.position = position
    self.hash_digest = hash_digest

  def get_hash(self):
    """
    Returns hash digest of leaf's value attribute.
    Returns:
      A string representing a hash digest.
    """
    # Don't rely on any pre-calculated values. Always calculate hash digest if raw value present.
    if self.value:
      return hashlib.sha256(self.value).hexdigest()
    elif self.hash_digest:
      return self.hash_digest
    else:
      raise Exception("Insufficient data: leaf %s is missing raw value and hash digest" % self.key)

  def to_dict(self):
    """
    Returns a dict representation of a leaf which is easily serializable to JSON.
    """
    return {"key": self.key,
            "value": self.value,
            "position": self.position,
            "hash_digest": self.hash_digest
            }


class ProofTree(object):

  def __init__(self):
    self.leaves = []

  def load_leaves(self, leaves_raw):
    """
    Loads Leaves from a list of dictionaries.
    """
    for leaf_raw in sorted(leaves_raw, key=lambda i: i["position"]):
      self.leaves.append(Leaf(**leaf_raw))

  def dump_leaves(self):
    """
    Returns a list of dict leaves.
    """
    return map(lambda leaf: leaf.to_dict(), self.leaves)

  def init_document(self, data):
    """
    Initializes Merkle tree leaves. We need to have a standardized way of doing this in order for
    tree root calculation to be idempotent.
    Args:
      data  - Dict of key/value pairs.
    """
    for i, (key, value) in enumerate(sorted(data.items())):
      leaf = Leaf(i, key, value)
      self.leaves.append(leaf)

  def is_valid(self, proof):
    """
    Checks if Merkle's tree root node equals a given proof.
    Args:
      proof  - String representing a proof.
    Returns:
      boolean
    """
    root_hash = self.get_root()
    return root_hash == proof

  def get_root(self):
    """
    Calculates Merkle tree root node value. In order to do this we need to have hash digest values
    for all leaves or their original values (from which we calculate hashes).
    """
    return self._get_root(self._get_leaf_hashes())

  def _get_root(self, nodes):
    """
    Helper function of get_root().
    """
    # Invalid input
    if not nodes:
      return None
    # At the root level - return!
    if len(nodes) == 1:
      return nodes[0]

    parent_nodes = []
    paired_nodes = chunks(nodes, 2)
    for pair in paired_nodes:
      hasher = hashlib.sha256()
      for element in pair:
        hasher.update(element)
      parent_nodes.append(hasher.hexdigest())
    return self._get_root(parent_nodes)

  def _get_leaf_hashes(self):
    """
    Returns a list of leaf hash digests. We always calculate them on the fly. We also make sure that
    returned list of hashes is in the right order as defined by leaf's position attribute.
    Returns:
      A list of hash digests.
    """
    return map(lambda leaf: leaf.get_hash(), sorted(self.leaves, key=lambda i: i.position))


def chunks(l, n):
  """
  Return n-sized chunks from a list.
  Args:
    l  - A list of elements.
    n  - Number defining the size of a chunk.
  Returns:
    A list of n-sized chunks.
  """
  return map(lambda i: l[i:i + n], xrange(0, len(l), n))
