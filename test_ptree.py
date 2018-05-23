import ptree
import unittest

TEST_DATA = {
  "photo": "https://avatars.org/johnsmith.jpg",
  "additionalName": "Smart",
  "addressCountry": "US",
  "addressLocality": "Mountain View",
  "addressRegion": "CA",
  "birthDate": "1981-19-05",
  "birthPlace": "San Francisco",
  "dateIssued": "2002-01-01",
  "documentID": "2178012",
  "expires": "2022-01-01",
  "familyName": "Smith",
  "gender": "M",
  "givenName": "John",
  "identificationNumber": "1905981500999",
  "nationality": "US",
  "postalCode": "94043"
}


class LeafTestCase(unittest.TestCase):

  def test_get_hash_should_calculate_hash_from_leaf_value(self):
    leaf = ptree.Leaf(0, "foo", "bar")
    self.assertEquals("fcde2b2edba56bf408601fb721fe9b5c338d10ee429ea04fae5511b68fbf8fb9",
                      leaf.get_hash())

  def test_get_hash_should_return_precalculated_hash(self):
    leaf = ptree.Leaf(0, "foo", None,
                    "fcde2b2edba56bf408601fb721fe9b5c338d10ee429ea04fae5511b68fbf8fb9")
    self.assertEquals("fcde2b2edba56bf408601fb721fe9b5c338d10ee429ea04fae5511b68fbf8fb9",
                      leaf.get_hash())

  def test_get_hash_should_raise_error_if_value_and_hash_digest_missing(self):
    leaf = ptree.Leaf(0, "foo")
    self.assertRaises(Exception, leaf.get_hash)


class ProofTreeTestCase(unittest.TestCase):

  def setUp(self):
    self.proof_tree = ptree.ProofTree()

  def test_load_leaves_should_load_data_from_dicts(self):
    data = [{"position": 0,
             "hash_digest": "fcde2b2edba56bf408601fb721fe9b5c338d10ee429ea04fae5511b68fbf8fb9",
             "key": "foo",
             "value": "bar"},
            {"position": 1,
             "hash_digest": "24fe93c9e17cb80452e5d86f1c186fc2fda2482cd5f81d7d305c2295bdab0aec",
             }
            ]
    self.proof_tree.load_leaves(data)
    self.assertEquals(2, len(self.proof_tree.leaves))

  def test_dump_leaves_should_return_leaves_as_dicts(self):
    data = {"foo": "bar", "a": "1"}
    expected = [{'hash_digest': None, 'key': 'a', 'position': 0, 'value': '1'},
                {'hash_digest': None, 'key': 'foo', 'position': 1, 'value': 'bar'}]
    self.proof_tree.init_document(data)
    actual = self.proof_tree.dump_leaves()
    self.assertListEqual(expected, actual)

  def test_init_document_should_set_empty_list(self):
    self.proof_tree.init_document({})
    self.assertEquals(0, len(self.proof_tree.leaves))

  def test_init_document_should_initialize_leaf(self):
    data = {"foo": "bar"}
    self.proof_tree.init_document(data)
    self.assertEquals(1, len(self.proof_tree.leaves))
    leaf = self.proof_tree.leaves[0]
    self.assertEquals("foo", leaf.key)
    self.assertEquals("bar", leaf.value)
    self.assertEquals(0, leaf.position)
    self.assertEquals(None, leaf.hash_digest)

  def test_init_document_should_initialize_multiple_leaves_in_correct_order(self):
    data = {"foo": "bar", "a": "1"}
    self.proof_tree.init_document(data)
    self.assertEquals(2, len(self.proof_tree.leaves))
    leaf_one = self.proof_tree.leaves[0]
    self.assertEquals("a", leaf_one.key)
    self.assertEquals(0, leaf_one.position)
    leaf_two = self.proof_tree.leaves[1]
    self.assertEquals("foo", leaf_two.key)
    self.assertEquals(1, leaf_two.position)

  def test__get_root_should_return_none_if_no_leaves(self):
    root_hash = self.proof_tree._get_root([])
    self.assertEquals(None, root_hash)

  def test__get_root_should_return_root_from_one_leaf(self):
    leaf_hash = "fcde2b2edba56bf408601fb721fe9b5c338d10ee429ea04fae5511b68fbf8fb9"
    root_hash = self.proof_tree._get_root([leaf_hash])
    self.assertEquals(leaf_hash, root_hash)

  def test__get_root_should_return_root_from_two_leaves(self):
    leaf_hash_one = "fcde2b2edba56bf408601fb721fe9b5c338d10ee429ea04fae5511b68fbf8fb9"
    leaf_hash_two = "d580754468330f66e5c155e16968a2be2a7828eca0885b42a0ce356594bfeab9"
    root_hash = self.proof_tree._get_root([leaf_hash_one, leaf_hash_two])
    self.assertEquals("1bbfb30fc434390e7a7256694d995c2a756c32a3d716a40a24842164bf86ccb5", root_hash)

  def test__get_root_should_return_root_from_three_leaves(self):
    leaf_hash_one = "fcde2b2edba56bf408601fb721fe9b5c338d10ee429ea04fae5511b68fbf8fb9"
    leaf_hash_two = "d580754468330f66e5c155e16968a2be2a7828eca0885b42a0ce356594bfeab9"
    leaf_hash_three = "bc7cf653fae92897cc99f396ae3aac58c03a4f7ced3d3bfe810b28e010b6623c"
    root_hash = self.proof_tree._get_root([leaf_hash_one, leaf_hash_two, leaf_hash_three])
    self.assertEquals("1a857260b79f9d209f201c635fb1cefae9e087af19a72642598eab112226b525", root_hash)

  def test__get_leaf_hashes_should_return_list_of_hashes(self):
    data = [{"position": 0,
             "hash": "fcde2b2edba56bf408601fb721fe9b5c338d10ee429ea04fae5511b68fbf8fb9",
             "key": "foo",
             "value": "bar"},
            {"position": 1,
             "hash": "31b0465400e7ca1352ce3f6f1688238458d1d021c8750620761089d91d82d089",
             "key": "moo",
             "value": "zar"}
            ]
    for leaf in data:
      self.proof_tree.leaves.append(ptree.Leaf(leaf["position"], leaf["key"], leaf["value"]))
    self.assertEquals([data[0]["hash"], data[1]["hash"]], self.proof_tree._get_leaf_hashes())

  def test_get_root_should_return_root_node_from_test_data(self):
    self.proof_tree.init_document(TEST_DATA)
    self.assertEquals("439518554dde3f594438a3fbcf028a24974e36153f345b98d74d803a82ecdd3c",
                      self.proof_tree.get_root())

  def test_is_valid_should_return_true_if_proof_the_same_as_root_node(self):
    self.proof_tree.init_document(TEST_DATA)
    proof = "439518554dde3f594438a3fbcf028a24974e36153f345b98d74d803a82ecdd3c"
    self.assertTrue(self.proof_tree.is_valid(proof))

  def test_is_valid_should_return_false_if_proof_not_the_same_as_root_node(self):
    self.proof_tree.init_document(TEST_DATA)
    proof = "XXX518554dde3f594438a3fbcf028a24974e36153f345b98d74d803a82ecdXXX"
    self.assertFalse(self.proof_tree.is_valid(proof))

  def test_should_validate_data_by_exposing_just_one_field(self):
    proof = "727747333f27c79c606c0c5a59882cbe3bd9c56d118664f679e10e79e4d1fad8"
    data = [{"position": 0,
             "hash_digest": "fcde2b2edba56bf408601fb721fe9b5c338d10ee429ea04fae5511b68fbf8fb9",
             "key": "foo",
             "value": "bar"},
            {"position": 1,
             "hash_digest": "24fe93c9e17cb80452e5d86f1c186fc2fda2482cd5f81d7d305c2295bdab0aec",
             }
            ]
    self.proof_tree.load_leaves(data)
    self.assertTrue(self.proof_tree.is_valid(proof))


class ChunksTestCase(unittest.TestCase):

  def test_chunks_should_return_none_if_input_empty_list(self):
    self.assertEquals([], ptree.chunks([], 2))

  def test_chunks_should_return_chunk_from_one_element_list(self):
    chunks = ptree.chunks([1], 2)
    self.assertEquals([[1]], chunks)

  def test_chunks_should_return_chunks_from_non_empty_list(self):
    chunks = ptree.chunks([1, 2, 3, 4, 5, 6], 2)
    self.assertEquals([[1, 2], [3, 4], [5, 6]], chunks)

  def test_chunks_should_return_chunks_from_odd_length_list(self):
    chunks = ptree.chunks([1, 2, 3, 4, 5, 6, 7], 2)
    self.assertEquals([[1, 2], [3, 4], [5, 6], [7]], chunks)
